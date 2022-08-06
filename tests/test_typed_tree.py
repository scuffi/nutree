# -*- coding: utf-8 -*-
# (c) 2021-2022 Martin Wendt; see https://github.com/mar10/nutree
# Licensed under the MIT license: https://www.opensource.org/licenses/mit-license.php
"""
"""
import re

from nutree.typed_tree import ANY_TYPE, TypedNode, TypedTree, _SystemRootTypedNode

from . import fixture


class TestTypedTree:
    def test_add_child(self):
        tree = TypedTree("fixture")
        assert not tree, "empty tree is falsy"
        assert tree.count == 0
        assert len(tree) == 0
        assert f"{tree}" == "TypedTree<'fixture'>"
        assert isinstance(tree._root, _SystemRootTypedNode)

        func = tree.add("func1", relation="function")

        assert isinstance(func, TypedNode)
        assert (
            re.sub(r"data_id=[-\d]+>", "data_id=*>", f"{func}")
            == "TypedNode<'function → func1', data_id=*>"
        )

        fail1 = func.add("fail1", relation="failure")

        fail1.add("cause1", relation="cause")
        fail1.add("cause2", relation="cause")

        fail1.add("eff1", relation="effect")
        fail1.add("eff2", relation="effect")

        func.add("fail2", relation="failure")

        func = tree.add("func2", relation="function")

        assert fixture.check_content(
            tree,
            """
            TypedTree<*>
            +- function → func1
            |  +- failure → fail1
            |  |  +- cause → cause1
            |  |  +- cause → cause2
            |  |  +- effect → eff1
            |  |  `- effect → eff2
            |  `- failure → fail2
            `- function → func2
           """,
        )

        assert fail1.first_child(relation="cause").name == "cause → cause1"
        assert fail1.last_child(relation="cause").name == "cause → cause2"
        assert fail1.first_child(relation="effect").name == "effect → eff1"
        assert fail1.last_child(relation="effect").name == "effect → eff2"
        assert fail1.first_child(relation=ANY_TYPE).name == "cause → cause1"
        assert fail1.last_child(relation=ANY_TYPE).name == "effect → eff2"

        assert len(fail1.children(relation=ANY_TYPE)) == 4
        assert len(fail1.children(relation="cause")) == 2
        assert fail1.children(relation="unknown") == []

        cause2 = tree["cause2"]
        assert cause2.get_siblings(any_type=True, add_self=True) == fail1.children(
            relation=ANY_TYPE
        )
        assert cause2.get_siblings() != fail1.children(relation=ANY_TYPE)
        assert cause2.get_siblings(add_self=True) == fail1.children(relation="cause")

    def test_graph(self):
        tree = TypedTree("fixture")

        alice = tree.add("Alice")
        bob = tree.add("Bob")

        alice.add("Carol", relation="friends")

        alice.add("Bob", relation="family")
        bob.add("Alice", relation="family")
        bob.add("Dan", relation="friends")

        # carol.add(bob, relation="friends")

        assert fixture.check_content(
            tree,
            """
            TypedTree<*>
            +- child → Alice
            |  +- friends → Carol
            |  `- family → Bob
            `- child → Bob
               +- family → Alice
               `- friends → Dan
           """,
        )

        # with fixture.WritableTempFile("w", suffix=".png") as temp_file:

        #     tree.to_dotfile(
        #         # temp_file.name,
        #         "/Users/martin/Downloads/tree.png",
        #         format="png",
        #         add_root=False,
        #         # node_mapper=node_mapper,
        #         # edge_mapper=edge_mapper,
        #         # unique_nodes=False,
        #     )
        #     assert False

    def test_graph_product(self):
        tree = TypedTree("Pencil")

        func = tree.add("Write on paper", relation="function")
        fail = func.add("Wood shaft breaks", relation="failure")
        fail.add("Unable to write", relation="effect")
        fail.add("Injury from splinter", relation="effect")
        fail.add("Wood too soft", relation="cause")

        fail = func.add("Lead breaks", relation="failure")
        fail.add("Cannot erase (dissatisfaction)", relation="effect")
        fail.add("Lead material too brittle", relation="cause")

        func = tree.add("Erase text", relation="function")

        assert fixture.check_content(
            tree,
            """
            TypedTree<*>
            +- function → Write on paper
            |  +- failure → Wood shaft breaks
            |  |  +- effect → Unable to write
            |  |  +- effect → Injury from splinter
            |  |  `- cause → Wood too soft
            |  `- failure → Lead breaks
            |     +- effect → Cannot erase (dissatisfaction)
            |     `- cause → Lead material too brittle
            `- function → Erase text
           """,
        )

        # with fixture.WritableTempFile("w", suffix=".png") as temp_file:

        #     tree.to_dotfile(
        #         # temp_file.name,
        #         "/Users/martin/Downloads/tree_graph_pencil.png",
        #         format="png",
        #         graph_attrs={"rankdir": "LR"},
        #         # add_root=False,
        #         # node_mapper=node_mapper,
        #         # edge_mapper=edge_mapper,
        #         # unique_nodes=False,
        #     )
        #     assert False
