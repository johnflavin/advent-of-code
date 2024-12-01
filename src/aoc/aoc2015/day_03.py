#!/usr/bin/env python
"""
PART 1
On a 2D grid, start at (0, 0)
Follow a sequence of directions (one of ^, v, <, or >)
How many unique points are visited?

PART 2
Split the sequence of directions into two sequences, the evens and the odds.
Follow both sequences from (0, 0).
How many unique points are visited?
"""
import itertools
from collections.abc import Iterable

from aoc.util import Coord


PART_ONE_EXAMPLE = """\
^>v<
"""
PART_ONE_EXAMPLE_RESULT = 4
PART_ONE_RESULT = 2572
PART_TWO_EXAMPLE = """\
^v^v^v^v^v
"""
PART_TWO_EXAMPLE_RESULT = 11
PART_TWO_RESULT = 2631


def follow_directions(directions: Iterable[str]) -> set[Coord]:
    points = [(0, 0)]
    for ch in directions:
        point = points[-1]
        if ch in "^v":
            new_point = (point[0], point[1] + (1 if ch == "^" else -1))
        elif ch in "<>":
            new_point = (point[0] + (1 if ch == ">" else -1), point[1])
        else:
            raise RuntimeError(f'Don\'t know what to do with character "{ch}"')
        points.append(new_point)
    return set(points)


def part_one(lines: Iterable[str]) -> int:
    line = list(lines)[0]
    points = follow_directions(line)
    return len(points)


def part_two(lines: Iterable[str]) -> int:
    line = list(lines)[0]
    points = follow_directions(itertools.islice(line, 0, None, 2))
    points.update(follow_directions(itertools.islice(line, 1, None, 2)))
    return len(points)
