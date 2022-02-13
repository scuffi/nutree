# -*- coding: utf-8 -*-
# (c) 2021-2022 Martin Wendt and contributors; see https://github.com/mar10/nutree
# Licensed under the MIT license: https://www.opensource.org/licenses/mit-license.php
"""
Implement diff/merge algorithms.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # Imported by type checkers, but prevent circular includes
    from .tree import Tree, Node

from enum import Enum


class DiffClassification(Enum):
    NEW = 1
    # ADDED = 1
    # REMOVED = 2
    MISSING = 2
    MOVED_HERE = 3
    MOVED_TO = 4
    SHIFTED = 5

    # REORDERED = 8
    # MODIFIED = 16


DC = DiffClassification


def _find_child(arr, child):
    """"""
    for i, c in enumerate(arr):
        if c == child:
            return (i, c)
    return (-1, None)


def diff_node_formatter(node):
    s = f"{node.name}"
    meta = node.meta
    if meta:
        flags = []
        v = meta.get("dc")
        if v:
            flags.append(f"{v}")
        if meta.get("dc_reordered"):
            flags.append("Children reordered")
        if meta.get("dc_cleared"):
            flags.append("Children cleared")
        flags = ", ".join(flags)
        s += f" - {flags}"

    return s


def diff_tree(t0: "Tree", t1: "Tree", *, sorted=True) -> "Tree":
    from nutree import Tree

    t2 = Tree(f"diff({t0.name!r}, {t1.name!r})")
    add_candidates = set()
    remove_candidates = set()

    def compare(p0: "Node", p1: "Node", p2: "Node"):
        p0_data_ids = set()
        for i0, c0 in enumerate(p0._children):
            p0_data_ids.add(c0._data_id)
            i1, c1 = _find_child(p1._children, c0)

            c2 = p2.add(c0)
            if i0 == i1:
                # Exact match of node and position
                pass
            elif c1:
                # Matching node, but at another position
                p2.set_meta("dc_reordered", True)
                c2.set_meta("dc", DC.SHIFTED)
            else:
                # t0 node is not found in t1
                c2.set_meta("dc", DC.MISSING)
                remove_candidates.add(c2._node_id)

            if c0._children:
                if c1:
                    if c1._children:
                        # c0 and c1 have children: Recursively visit peer nodes
                        compare(c0, c1, c2)
                    else:
                        # c0 has children and c1 exists, but has no children
                        # TODO: copy children c0 to c2
                        c2.set_meta("dc_cleared", True)
                else:
                    # c0 has children, but c1 does not even exist
                    # TODO: Copy children from c0 to c2, but we need to check
                    #       if c1 is really removed or just moved-away
                    pass
            elif c1:
                if c1._children:
                    # c1 has children and c0 exists, but has no children
                    # TODO: copy children c1 to c2
                    pass
                else:
                    # Neither c0 nor c1 have children: Nothing to do
                    pass

        # Collect t1 nodes that are not in t0:
        for c1 in p1._children:
            if c1._data_id not in p0_data_ids:
                c2 = p2.add(c1)
                c2.set_meta("dc", DC.NEW)
                add_candidates.add(c2._node_id)
                if c1._children:
                    # c1 has children, but c0 does not even exist
                    # TODO: Copy children from c1 to c2, but we need to check
                    #       if c1 is really added or just moved-here
                    pass
                else:
                    # c1 does not have children and c0 does not exist:
                    # We already marked a 'new', nothing more to do.
                    pass

    compare(t0._root, t1._root, t2._root)
    return t2
