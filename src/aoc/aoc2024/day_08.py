#!/usr/bin/env python
"""
PART 1
Given a grid of antennas (lower, upper, and digits)
Pairs of antennae create "antinodes" at locations
in line with the pair where one is twice as far as another.
Antinodes can colocate with an antenna, and can overlap.
However, we do not count them if they are outside the grid.
How many locations on the grid have antinodes?

PART 2
Now antinodes occur at every location that is n*(p1 - p2)
from a pair.
"""
import itertools
import logging
from collections import defaultdict
from collections.abc import Iterable

from aoc.util import Pt, add, sub


PART_ONE_EXAMPLE = """\
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
"""
PART_ONE_EXAMPLE_RESULT = 14
PART_ONE_RESULT = 285
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 34
PART_TWO_RESULT = 944


log = logging.getLogger(__name__)


type AntennaLocs = dict[str, set[Pt]]


def debug_log(
    antenna_locs: dict[str, set[Pt]],
    antinode_locs: set[Pt],
    max_x: int,
    max_y: int,
) -> None:
    if not log.isEnabledFor(logging.DEBUG):
        return

    def find_symbol(c: Pt) -> str:
        for antenna, locs in antenna_locs.items():
            if c in locs:
                return antenna
        if c in antinode_locs:
            return "#"
        return "."

    for y in range(max_y):
        log.debug("".join(find_symbol((x, y)) for x in range(max_x)))


def parse(lines: Iterable[str]) -> tuple[AntennaLocs, int, int]:
    locs = defaultdict(set)
    x = 0
    y = 0
    for y, line in enumerate(lines):
        if not line:
            continue
        for x, ch in enumerate(line):
            if ch != ".":
                locs[ch].add((x, y))

    return locs, x + 1, y + 1


def part_one(lines: Iterable[str]) -> int:
    antenna_locs, max_x, max_y = parse(lines)
    log.debug("max_x=%d max_y=%d", max_x, max_y)
    debug_log(antenna_locs, set(), max_x, max_y)
    log.debug("-----")

    def inbounds(p: Pt) -> bool:
        return 0 <= p[0] < max_x and 0 <= p[1] < max_y

    antinode_locs = set()
    for antenna, locs in antenna_locs.items():
        for p1, p2 in itertools.combinations(locs, 2):
            delta = sub(p1, p2)
            an1 = add(p1, delta)  # 2*p1 - p2
            an2 = sub(p2, delta)  # 2*p2 - p1
            antinode_locs.update(an for an in (an1, an2) if inbounds(an))
    debug_log(antenna_locs, antinode_locs, max_x, max_y)

    return len(antinode_locs)


def part_two(lines: Iterable[str]) -> int:
    antenna_locs, max_x, max_y = parse(lines)
    log.debug("max_x=%d max_y=%d", max_x, max_y)
    debug_log(antenna_locs, set(), max_x, max_y)
    log.debug("-----")

    def inbounds(p: Pt) -> bool:
        return 0 <= p[0] < max_x and 0 <= p[1] < max_y

    antinode_locs = set()
    for antenna, locs in antenna_locs.items():
        for p1, p2 in itertools.combinations(locs, 2):
            delta = sub(p1, p2)
            # Add p1
            antinode_locs.add(p1)
            # Add points for non-negative delta
            an = p1
            while inbounds(an := add(an, delta)):
                antinode_locs.add(an)
            # Add points for negative delta
            an = p1
            while inbounds(an := sub(an, delta)):
                antinode_locs.add(an)
    debug_log(antenna_locs, antinode_locs, max_x, max_y)

    return len(antinode_locs)
