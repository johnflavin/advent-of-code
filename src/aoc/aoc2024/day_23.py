#!/usr/bin/env python
"""
PART 1
Given sets of connections xx-yy between computers
find sets of three interconnected computers where at least
one of the names has a t

PART 2
Find biggest clique in connection graph
"""
from collections.abc import Iterable

import networkx as nx


PART_ONE_EXAMPLE = """\
kh-tc
qp-kh
de-cg
ka-co
yn-aq
qp-ub
cg-tb
vc-aq
tb-ka
wh-tc
yn-cg
kh-ub
ta-co
de-co
tc-td
tb-wq
wh-td
ta-ka
td-qp
aq-cg
wq-ub
ub-vc
de-ta
wq-aq
wq-vc
wh-yn
ka-de
kh-ta
co-tc
wh-qp
tb-vc
td-yn
"""
PART_ONE_EXAMPLE_RESULT = 7
PART_ONE_RESULT = 1173
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = "co,de,ka,ta"
PART_TWO_RESULT = "cm,de,ez,gv,hg,iy,or,pw,qu,rs,sn,uc,wq"


def part_one(lines: Iterable[str]) -> int:
    g = nx.Graph([line.split("-") for line in lines])
    return sum(
        any(conn.startswith("t") for conn in cycle)
        for cycle in nx.simple_cycles(g, length_bound=3)
    )


def part_two(lines: Iterable[str]) -> str:
    g = nx.Graph([line.split("-") for line in lines])
    largest_clique = max(nx.find_cliques(g), key=len)
    return ",".join(sorted(largest_clique))
