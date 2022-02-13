# -*- coding: utf-8 -*-
# (c) 2021-2022 Martin Wendt; see https://github.com/mar10/nutree
# Licensed under the MIT license: https://www.opensource.org/licenses/mit-license.php
"""
"""
from nutree.diff import diff_node_formatter

from . import fixture


class TestDiff:
    def test_diff(self):

        tree_0 = fixture.create_tree(name="T0")

        tree_0["a2"].add("a21_left")

        tree_1 = fixture.create_tree(name="T1")

        tree_1["a2"].add("a21_right")
        tree_1["a11"].remove()
        tree_1.add_child("C")

        tree_2 = tree_0.diff(tree_1)

        tree_2.print(repr=diff_node_formatter)

        assert fixture.check_content(
            tree_2,
            """
            Tree<*>
            +- A
            |  +- a1
            |  |  +- a11
            |  |  `- a12
            |  `- a2
            |     +- a21_left
            |     `- a21_right
            +- B
            |  `- b1
            |     `- b11
            `- C
            """,
        )
