# -*- coding: utf-8 -*-
# (c) 2021-2022 Martin Wendt and contributors; see https://github.com/mar10/nutree
# Licensed under the MIT license: https://www.opensource.org/licenses/mit-license.php
"""
Methods to support reading and writing of 
`RDF <https://en.wikipedia.org/wiki/Resource_Description_Framework>`_ formats.
"""
from nutree import Tree

try:
    from rdflib import Graph, URIRef, Literal, BNode
    from rdflib.namespace import FOAF, RDF
except ImportError:
    rdflib = None


def _assert_rdflib():
    if not rdflib:
        raise RuntimeError("Need rdflib installed to handle RDF formats.")


def tree_to_graph(tree: Tree):
    """"""
    _assert_rdflib()
    graph = rdflib.Graph()
    # for node in tree:


def read_tree(path: str):
    g = Graph()
    result = g.parse("http://www.w3.org/2000/10/swap/test/meet/blue.rdf")




def write_tree(tree: Tree):
    """"""
    graph = tree_to_graph(tree)
    print(graph.serialize())
    iri = "http://wwwendt.de/iri/nutree"
