#!/usr/bin/env python
"""

PART 1
Given a map of connected components.
Find three wires you need to disconnect in order to
divide the components into two separate groups.
Multiply the sizes of the groups together.

PART 2
"""
from collections.abc import Iterable

import networkx as nx


PART_ONE_EXAMPLE = """\
jqt: rhn xhk nvd
rsh: frs pzl lsr
xhk: hfx
cmg: qnr nvd lhk bvb
rhn: xhk bvb hfx
bvb: xhk hfx
pzl: lsr hfx nvd
qnr: nvd
ntq: jqt hfx bvb xhk
nvd: lhk
lsr: lhk
rzs: qnr cmg lsr rsh
frs: qnr lhk lsr
"""
PART_ONE_EXAMPLE_RESULT = 54
PART_ONE_RESULT = 543256
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = -1


def parse_lines_to_graph(lines: Iterable[str]) -> nx.Graph:
    def line_split(line):
        l_node, rhs = line.split(": ")
        for r_node in rhs.split():
            yield l_node, r_node

    g = nx.Graph()
    g.add_edges_from(edge for line in lines for edge in line_split(line))
    return g


def part_one(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    G = parse_lines_to_graph(lines)

    bisection = nx.spectral_bisection(G)

    if len(bisection) != 2:
        raise RuntimeError("Did not find correct cut")

    return len(bisection[0]) * len(bisection[1])


def part_two(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    return -1
