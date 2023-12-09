#!/usr/bin/env python
"""

PART 1
Given a sequence of Rs and Ls, which are "right" and "left" instructions.
Then a sequence of nodes, which connect to other nodes.
Starting from node AAA and following the instructions, repeating the
sequence if you run out, how many
steps does it take to reach ZZZ?

Notes:
Don't do anything clever here. It's the halting problem. Just run it.

PART 2
Start on all nodes that end in A.
Using the sequence of Rs and Ls, simultaneously move
through all the steps until all nodes end in Zs.

Notes:
This one isn't finishing in a reasonable time. Now is time for the cleverness.
Because this isn't the halting problem anymore. It's about figuring out
when each of these independent processes would halt together.

I don't know exactly how to find the cycles, or what I would do with them.
I am pretty sure that if any cycles do exist, they have to have the same period,
which is the length of the instructions.
Wait, is that true? That can't be true. Because if they all have the same period
then they would be in sync every time.
And I can tell from looking at some debug output that they all have some periodic
behavior, they all are hitting some Z node repeatedly.

So let's say I detect a cycle in one of the threads. It hits the same Z node
on steps s1 and s2. Its period is p = s2-s1. I know that in the future it will
hit the Z node again at s1 + p*k for every non-negative k.

So I need to find some step number S that simultaneously solves N equations
of the form s1_i + p_i*k_i. I can measure s1_i and p_i but I don't know any k_i.
What can I say about this number S?
I know S - s1_i is a multiple of p_i.
But how do I use that information?
Does this get easier as a linear algebra problem?
No, not really. The ps and ks aren't a matrix or anything, just another vector.

What I need is for one of the cycles to start at phase zero. Then I know the answer is
a multiple of that p.

How about this...
Rank the cycles according to the s1s, so the smallest s1 is s1_0.
Subtract it out of all the other s1s.
That gives us a cycle that starts at 0.
Now we know that all the cycles starting from their adjusted phases will hit
a multiple of that p at some point.
Does that matter?

Ran an experiment to find s1 and p
5 s1=11911
4 s1=13019
2 s1=14681
3 s1=16897
1 s1=19667
0 s1=21883
5 s1=11911 p=11911
4 s1=13019 p=13019
2 s1=14681 p=14681
3 s1=16897 p=16897
1 s1=19667 p=19667
0 s1=21883 p=21883
Turns out... there is no s!! They all start at zero phase!

Ok, so they all start at 0 and just have different periods p.
So how do I find where all those p intersect?
Well, let's think about this... They are all products of primes.
If they all have some prime(s) in common in their factorization, then that'll be
in the answer. As will every other prime that is not in common in their factorizations.
But just one of each.
...
This is too complicated. Let's just think about a pair.
Multiply them together, and the two cycles will definitely intersect there.
But they might intersect sooner, if they share any factors.
Find the gcd of the pair, divide that out of the product.
That's the first number where both cycles intersect.
Now do that process again with the others.
Given the intersection number of the first two, find the intersection number
with that and the next cycle period (multiply, then divide by gcd).
Once we've done that with all of them, we have found our step number.

Later note: Turns out this is just lcm. Who knew?
"""

from collections.abc import Iterable
from itertools import cycle
from math import lcm


PART_ONE_EXAMPLE = """\
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)
"""
PART_ONE_EXAMPLE_RESULT = 2
PART_ONE_RESULT = 11911
PART_TWO_EXAMPLE = """\
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
"""
PART_TWO_EXAMPLE_RESULT = 6
PART_TWO_RESULT = 10151663816849


def just_keep_walking(steps: str, node_map: dict[str, str]) -> int:
    node = "AAA"
    for step, direction in enumerate(cycle(steps), 1):
        next_node = node_map[node + direction]
        if next_node == "ZZZ":
            return step
        node = next_node


def just_stop_walking(steps: str, nodes: list[str], node_map: dict[str, str]) -> int:
    cycles = [0] * len(nodes)
    for step, direction in enumerate(cycle(steps), 1):
        next_nodes = [node_map[node + direction] for node in nodes]

        for i, next_node in enumerate(next_nodes):
            if next_node[-1] == "Z":
                if cycles[i] == 0:
                    cycles[i] = step
        if all(cycles):
            break

        nodes = next_nodes

    return lcm(*cycles)


def parse(lines: Iterable[str]) -> tuple[str, dict[str, str]]:
    lines = iter(lines)
    steps = next(lines)
    next(lines)  # blank

    node_map = {}
    for line in lines:
        node, mapping = line.split(" = ")
        left, right = mapping[1:-1].split(", ")
        node_map[node + "L"] = left
        node_map[node + "R"] = right

    return steps, node_map


def part_one(lines: Iterable[str]) -> int:
    steps, node_map = parse(lines)
    return just_keep_walking(steps, node_map)


def part_two(lines: Iterable[str]) -> int:
    steps, node_map = parse(lines)
    a_nodes = [node[0:3] for node in node_map if node[2:] == "AL"]
    return just_stop_walking(steps, a_nodes, node_map)
