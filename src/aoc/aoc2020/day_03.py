#!/usr/bin/env python
"""
PART 1
Given a grid of trees (cylindrical coords)
A toboggan moves down with some slope.
(I bet part 2 is finding one that doesn't hit a tree...)
Go with slope (3, 1) and count how many trees you hit.

PART 2
Do part 1 for a few slopes and multiply the results
"""
import math
from collections.abc import Iterable

from aoc.util import Pt


PART_ONE_EXAMPLE = """\
..##.......
#...#...#..
.#....#..#.
..#.#...#.#
.#...##..#.
..#.##.....
.#.#.#....#
.#........#
#.##...#...
#...##....#
.#..#...#.#
"""
PART_ONE_EXAMPLE_RESULT = 7
PART_ONE_RESULT = 232
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 336
PART_TWO_RESULT = 3952291680


def parse(lines: Iterable[str]) -> tuple[int, int, set[Pt]]:
    trees = set()
    max_x = 0
    max_y = 0
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == "#":
                trees.add((x, y))
            if x >= max_x:
                max_x = x + 1
        if y >= max_y:
            max_y = y + 1
    return max_x, max_y, trees


def count_tree_hits(slope: Pt, max_x: int, max_y: int, trees: set[Pt]) -> int:
    pt = (0, 0)
    hit = 0
    while pt[1] < max_y:
        if pt in trees:
            hit += 1
        pt = ((pt[0] + slope[0]) % max_x, pt[1] + slope[1])
    return hit


def part_one(lines: Iterable[str]) -> int:
    max_x, max_y, trees = parse(lines)
    return count_tree_hits((3, 1), max_x, max_y, trees)


def part_two(lines: Iterable[str]) -> int:
    max_x, max_y, trees = parse(lines)
    return math.prod(
        count_tree_hits(slope, max_x, max_y, trees)
        for slope in ((1, 1), (3, 1), (5, 1), (7, 1), (1, 2))
    )
