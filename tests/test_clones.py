# -*- coding: utf-8 -*-
# (c) 2021-2022 Martin Wendt and contributors; see https://github.com/mar10/nutree
# Licensed under the MIT license: https://www.opensource.org/licenses/mit-license.php
"""
"""
import pytest

from nutree import AmbigousMatchError, Node, Tree

from . import fixture

# class Item:
#     def __init__(self, name, price, count):
#         self.name = name
#         self.price = float(price)
#         self.count = int(count)

#     def __repr__(self):
#         return f"Item<{self.name!r}, {self.price:.2f}$>"


class TestClones:
    def setup_method(self):
        self.tree = Tree("fixture")

    def teardown_method(self):
        self.tree = None

    def test_clones(self):
        """ """
        tree = fixture.create_tree()

        # Add another 'a1' below 'B'
        tree["B"].add("a1")
        print(tree.format(repr="{node.data}"))

        # tree[data] expects single matches
        with pytest.raises(KeyError):
            tree.__getitem__("not_existing")
        with pytest.raises(AmbigousMatchError):
            tree.__getitem__("a1")

        res = tree.find("a1")
        assert res.data == "a1"

        res = tree.find("not_existing")
        assert res is None

        assert not tree["a2"].is_clone()

        res = tree.find_all("a1")

        assert res[0].is_clone()
        assert res[1].is_clone()

        assert len(res) == 2
        assert isinstance(res[0], Node)
        assert res[0] == res[1]  # nodes are equal
        assert res[0] == res[1].data  # nodes are equal
        assert res[0] is not res[1]  # but not identical
        assert res[0].data == res[1].data  # node.data is equal
        assert res[0].data is res[1].data  # and identical

        res = tree.find_all("not_existing")
        assert res == []

        assert tree._self_check()