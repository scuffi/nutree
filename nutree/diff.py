# -*- coding: utf-8 -*-
# (c) 2021-2022 Martin Wendt and contributors; see https://github.com/mar10/nutree
# Licensed under the MIT license: https://www.opensource.org/licenses/mit-license.php
"""
Implement diff/merge algorithms.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # Imported by type checkers, but prevent circular includes
    from .tree import Tree


def diff_tree(t0: "Tree", t1: "Tree") -> "Tree":
    pass
