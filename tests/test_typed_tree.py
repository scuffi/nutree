# -*- coding: utf-8 -*-
# (c) 2021-2022 Martin Wendt; see https://github.com/mar10/nutree
# Licensed under the MIT license: https://www.opensource.org/licenses/mit-license.php
"""
"""
import re
from nutree.typed_tree import _SystemRootTypedNode, TypedNode, TypedTree

from . import fixture


class TestTypedTree:
    def test_add_child(self):
        tree = TypedTree("fixture")
        assert not tree, "empty tree is falsy"
        assert tree.count == 0
        assert len(tree) == 0
        assert f"{tree}" == "TypedTree<'fixture'>"
        assert isinstance(tree._root, _SystemRootTypedNode)

        func = tree.add("func1", type="function")

        assert isinstance(func, TypedNode)
        assert (
            re.sub(r"data_id=[-\d]+>", "data_id=*>", f"{func}")
            == "TypedNode<'function → func1', data_id=*>"
        )

        fail = func.add("fail1", type="failure")

        fail.add("cause1", type="cause")
        fail.add("cause2", type="cause")

        fail.add("eff1", type="effect")
        fail.add("eff2", type="effect")

        fail = func.add("fail2", type="faiure")

        func = tree.add("func2", type="function")

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
            |  `- faiure → fail2
            `- function → func2
           """,
        )
