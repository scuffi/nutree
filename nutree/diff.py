# -*- coding: utf-8 -*-
# (c) 2021-2022 Martin Wendt and contributors; see https://github.com/mar10/nutree
# Licensed under the MIT license: https://www.opensource.org/licenses/mit-license.php
"""
Implement diff/merge algorithms.
"""
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:  # Imported by type checkers, but prevent circular includes
    from .tree import Tree, Node

from enum import Enum


class DiffClassification(Enum):
    ADDED = 1
    REMOVED = 2
    MOVED_HERE = 3
    MOVED_TO = 4


#: Alias for DiffClassification
DC = DiffClassification


class ChangeRecorder:
    """
    Context manager to collect intermediate tree modifications.

    **Experimental**

    Examples:
        with tree.change_recorder() as rec:
            tree["a2"].add("a21")
            tree["a11"].remove()
            ...

        rec.get_diff_tree().print(repr=diff_node_formatter)
        patch = rec.get_patch()

    """

    def __init__(self, tree: "Tree"):
        self._tree: "Tree" = tree
        self._org_copy: "Tree" = None
        self._diff_tree: "Tree" = None

    def __repr__(self):
        state = "unresolved" if self._diff_tree is None else f"{len(self._diff_tree)}"
        return f"{self.__class__.__name__}<{self._tree}, delta={state}>"

    def __enter__(self):
        with self._tree:
            self._org_copy = self._tree.copy(name=f"Snapshot of {self._tree}")
        return self

    def __exit__(self, type, value, traceback):
        # self._diff_tree = self._org_copy.diff(self._tree, reduce=True)
        self._diff_tree = diff_tree(
            self._org_copy, self._tree, reduce=True, add_ref_info=True
        )
        # self._org_copy = None
        return

    def get_diff_tree(self) -> "Tree":
        assert self._diff_tree, "Available after context manager exited."
        return self._diff_tree

    def get_patch(self) -> list:
        iter = iter_changes_as_patch(self.get_diff_tree())
        return list(iter)


def _find_child(arr, child):
    for i, c in enumerate(arr):
        if c == child:
            return (i, c)
    return (-1, None)


def _copy_children(source: "Node", dest: "Node", add_set: set, meta: tuple) -> None:
    assert source.has_children() and not dest.has_children()
    for n in source.children:
        n_dest = dest.append_child(n)
        add_set.add(n_dest._node_id)
        if meta:
            n_dest.set_meta(*meta)
        if n._children:
            # meta is only set on top node
            _copy_children(n, n_dest, add_set, meta=None)
    return


def diff_node_formatter(node):
    """Use with :meth:`~nutree.tree.format` or :meth:`~nutree.tree.print`
    `repr=...` arguments."""
    s = f"{node.name}"
    meta = node.meta

    if meta:
        flags = []
        dc = meta.get("dc")
        if dc is None:
            pass
        elif dc == DC.ADDED:
            flags.append("Added")  # ☆ 🌟
        elif dc == DC.REMOVED:
            flags.append("Removed")  # × ❌
        elif dc == DC.MOVED_HERE:
            flags.append("Moved here")  # ←
        elif dc == DC.MOVED_TO:
            flags.append("Moved away")  # ×➡
        elif type(dc) is tuple:  # == DC.SHIFTED:
            ofs = dc[1] - dc[0]
            flags.append(f"Order {ofs:+d}")  # ⇳ ⇵
            # flags.append("Shifted")  # ⇳ ⇵
        elif dc:
            flags.append(f"{dc}")

        if meta.get("dc_renumbered"):
            flags.append("Renumbered")
        if meta.get("dc_cleared"):
            flags.append("Children cleared")

        flags = "[" + "], [".join(flags) + "]"
        s += f" - {flags}"

    return s


def diff_tree(
    t0: "Tree", t1: "Tree", *, ordered=False, reduce=False, add_ref_info=False
) -> "Tree":
    """Compare t0 against t1 and return a merged, annotated tree copy.

    The resulting tree ('t2') contains a union of all nodes from t0 and t1.
    Additional metadata is added to the resulting nodes to classify changes
    from the perspective of t0. For example a node that only exists
    in t1, will have ``node.get_meta("dc") == DiffClassification.ADDED``
    defined.

    Nodes are considered equal if node pairs are located in equivalent structure
    locations and ``a == b`` resolves to true. |br|
    If `ordered` is true, changes in the child order are also considered a
    change.

    If `reduce` is true, unchanged nodes are removed, leaving a compact tree
    with only the modifications.

    `add_ref_info` adds aditional node references to the meta data, e.g.
    the parent node for 'add' operations.

    TODO:
    If the `compare_nodes` argument contains a method, it will be called for
    every node pair. It must be a method that accepts
    two `Node` instances and returns a comparison result. |br|
    A return value of `None` or `False` means 'nodes are equal.
    Other values are interpreted as 'nodes are unequal'.

    See :ref:`Diff and Merge` for details.
    """
    from nutree import Tree

    t2 = Tree(f"diff({t0.name!r}, {t1.name!r})")
    added_nodes = set()
    removed_nodes = set()

    def compare(p0: "Node", p1: "Node", p2: "Node"):
        p0_data_ids = set()
        # `p0.children` always returns an (possibly empty) array
        for i0, c0 in enumerate(p0.children):
            p0_data_ids.add(c0._data_id)
            i1, c1 = _find_child(p1._children, c0)

            c2 = p2.add(c0)

            if i0 == i1:
                # Exact match of node and position
                pass
            elif c1:
                # Matching node, but at another position
                if ordered:
                    p2.set_meta("dc_renumbered", True)
                    c2.set_meta("dc", (i0, i1))
            else:
                # t0 node is not found in t1
                c2.set_meta("dc", DC.REMOVED)
                removed_nodes.add(c2._node_id)
                if add_ref_info:
                    # c2.set_meta("dc_t0_node", c0)
                    c2.set_meta("dc_t1_parent_node_id", p1.node_id)
                    c2.set_meta("dc_t1_data_id", c2.data_id)
                    # c2.set_meta("dc_t1_node_id", c1.node_id)

            if c0._children:
                if c1:
                    compare(c0, c1, c2)
                    # if c1._children:
                    #     # c0 and c1 have children: Recursively visit peer nodes
                    #     compare(c0, c1, c2)
                    # else:
                    #     # c0 has children and c1 exists, but has no children
                    #     # TODO: copy children c0 to c2
                    #     c2.set_meta("dc_cleared", True)
                else:
                    # c0 has children, but c1 does not even exist
                    # TODO: Copy children from c0 to c2, but we need to check
                    #       if c1 is really removed or just moved-away
                    pass
            elif c1:
                if c1._children:
                    # c1 has children and c0 exists, but has no children
                    compare(c0, c1, c2)
                else:
                    # Neither c0 nor c1 have children: Nothing to do
                    pass

        # print(p1, p1._children, p0_data_ids)

        # Collect t1 nodes that are not in t0:
        for c1 in p1.children:  # `p1.children` always returns an (possibly empty) array
            # print("  ", c1, c1._data_id in p0_data_ids)
            if c1._data_id not in p0_data_ids:
                c2 = p2.add(c1)
                c2.set_meta("dc", DC.ADDED)
                added_nodes.add(c2._node_id)
                if add_ref_info:
                    c2.set_meta("dc_t1_node", c1)
                if c1._children:
                    # c1 has children, but c0 does not even exist
                    # TODO: Copy children from c1 to c2, but we need to check
                    #       if c1 is really added or just moved-here
                    _copy_children(c1, c2, added_nodes, ("dc", DC.ADDED))
                else:
                    # c1 does not have children and c0 does not exist:
                    # We already marked a 'new', nothing more to do.
                    pass
        return  # End of `def compare()`

    compare(t0._root, t1._root, t2._root)

    # Re-classify: check added/removed nodes for move operations
    # print(added_nodes)
    # print(removed_nodes)
    for nid in added_nodes:
        added_node = t2._node_by_id[nid]
        # print(added_node)
        other_clones = added_node.get_clones()
        # print(other_clones)
        removed_clones = [n for n in other_clones if n.get_meta("dc") == DC.REMOVED]
        if removed_clones:
            added_node.set_meta("dc", DC.MOVED_HERE)
            for n in removed_clones:
                n.set_meta("dc", DC.MOVED_TO)

    # Purge unchanged parts from tree
    if reduce:

        def pred(node):
            return bool(node.get_meta("dc"))

        t2.filter(predicate=pred)

    return t2


def iter_changes_as_patch(tree: "Tree") -> Generator[dict, None, None]:
    """Yield a sequence of changes.

    **Experimental**
    Every change is passed as dict.

    Args:
        tree (Tree): typically the result of a previous call to :meth:`~nutree.tree.Tree.diff`
    """
    # Assuming
    #     t0   is the temporary snapshot copy, that a ChangeRecorder created
    #     t1   is the original tree instance that now has changes applied
    #     tree is the temporary diff-tree (shallow, filtered merge of t0 and t1)
    for node in tree:
        # flags = []
        dc = node.get_meta("dc")
        if dc is None:
            continue
        res = {"_key": node.node_id, "_name": node.name}  # , "dc": dc}

        if dc in (DC.ADDED, DC.MOVED_HERE):
            ref_node = node.get_meta("dc_t1_node")
            res.update(
                {
                    "type": "add",
                    "node_id": ref_node.node_id if ref_node else None,
                    "node": ref_node,
                }
            )
        elif dc in (DC.REMOVED, DC.MOVED_TO):
            # ref_node = node.get_meta("dc_t0_node")
            res.update(
                {
                    "type": "remove",
                    "parent_id": node.get_meta("dc_t1_parent_node_id"),
                    "data_id": node.get_meta("dc_t1_data_id"),
                }
            )
        else:
            continue

        yield res
    return
