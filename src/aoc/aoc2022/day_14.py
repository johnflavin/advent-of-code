#!/usr/bin/env python
"""
PART 1
Our input is a set of definitions for rock walls in an x-z plane
(where positive z goes down and positive x goes right).
Sand is produced at 500,0 and falls until blocked by rocks or sand.
Once blocked, it tries to go down-left, then down right, and finally
stops.
Once it stops another grain of sand is produced at 500, 0.
Eventually the space fills up and all new sand falls off into the void.
How many grains of sand are in the space when it fills?

PART 2
There is no void, there is a floor two z below the lowest rocks (infinite in x).
Sand flows until a grain comes to rest at (500, 0).
"""
import itertools
import logging
import math
from collections.abc import Iterable

from aoc.util import Pt


PART_ONE_EXAMPLE = """\
498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
"""
PART_ONE_EXAMPLE_RESULT = 24
PART_ONE_RESULT = 757
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 93
PART_TWO_RESULT = 24943


log = logging.getLogger(__name__)


def debug_draw(
    rocks: set[Pt], sand: set[Pt], x_min: int, x_max: int, z_max: int
) -> None:
    if not log.isEnabledFor(logging.DEBUG):
        return

    # Figure out the size and position of the labels
    num_z_digits = round(math.log10(z_max))
    num_x_digits = round(math.log10(x_max))
    gap_edge_x_min = num_z_digits + 2
    gap_x_min_500 = 500 - x_min
    gap_500_x_max = x_max - 500
    for x_min_digit, sand_digit, x_max_digit in zip(
        str(x_min), f"{500: >{num_x_digits}}", str(x_max)
    ):
        log.debug(
            f"{x_min_digit: >{gap_edge_x_min}}"
            + f"{sand_digit: >{gap_x_min_500}}"
            + f"{x_max_digit: >{gap_500_x_max}}"
        )
    for z in range(0, z_max + 1):
        stuff = [
            "#" if (x, z) in rocks else "o" if (x, z) in sand else "."
            for x in range(x_min, x_max + 1)
        ]
        log.debug(f"{z: >{num_z_digits}} {"".join(stuff)}")


def parse(line: str) -> Iterable[Pt]:
    line_ends = [
        tuple(int(c) for c in line_end_str.split(","))
        for line_end_str in line.split(" -> ")
    ]

    for end0, end1 in itertools.pairwise(line_ends):
        if end0[0] == end1[0]:
            step = 1 if end0[1] < end1[1] else -1
            yield from ((end0[0], z) for z in range(end0[1], end1[1], step))
        elif end0[1] == end1[1]:
            step = 1 if end0[0] < end1[0] else -1
            yield from ((x, end0[1]) for x in range(end0[0], end1[0], step))
    # Last point will not be included in a range, so yield it separately
    yield line_ends[-1]


def find_rock_limits(rocks: set[Pt]) -> tuple[int, int, int]:
    """Find the limits of the rocks: the max and min x values,
    and the lowest z value"""
    x_min = 500
    x_max = 500
    z_max = 0
    for x, z in rocks:
        if x < x_min:
            x_min = x
        elif x > x_max:
            x_max = x
        if z > z_max:
            z_max = z
    return x_min, x_max, z_max


def place_sand(
    rocks: set[Pt],
    sand: set[Pt],
    x_min: int,
    x_max: int,
    z_max: int,
    floor: bool = False,
) -> bool:
    """Add a grain of sand at 500,0 and follow the rules.
    If it comes to rest, add it to the sand list and return True.
    If it falls off the edge, return False."""
    while True:
        # Start a new grain
        grain = (500, 0)
        while floor or x_min - 1 <= grain[0] <= x_max + 1 and z_max > grain[1]:
            for try_next in (
                (grain[0], grain[1] + 1),
                (grain[0] - 1, grain[1] + 1),
                (grain[0] + 1, grain[1] + 1),
            ):
                if (
                    try_next not in rocks
                    and try_next not in sand
                    and (not floor or try_next[1] < z_max + 2)
                ):
                    # Nothing stopping us
                    grain = try_next
                    break
            else:
                # We didn't find a safe next spot. Grain rests at current location.
                log.debug("Sand grain comes to rest at %s", grain)
                sand.add(grain)
                return True

        # We have fallen into the void
        log.debug("Grain fell into the void at %s. All done!", grain)
        return False


def part_one(lines: Iterable[str]) -> int:
    rocks = set(itertools.chain.from_iterable(parse(line) for line in lines if line))
    sand = set()
    x_min, x_max, z_max = find_rock_limits(rocks)
    is_debug = log.isEnabledFor(logging.DEBUG)
    if is_debug:
        debug_draw(rocks, sand, x_min, x_max, z_max)
    while place_sand(rocks, sand, x_min, x_max, z_max):
        if is_debug:
            log.debug("Grain %d", len(sand))
            debug_draw(rocks, sand, x_min, x_max, z_max)
    return len(sand)


def part_two(lines: Iterable[str]) -> int:
    rocks = set(itertools.chain.from_iterable(parse(line) for line in lines if line))
    sand = set()
    x_min, x_max, z_max = find_rock_limits(rocks)
    is_debug = log.isEnabledFor(logging.DEBUG)
    if is_debug:
        debug_draw(rocks, sand, x_min, x_max, z_max)
    while place_sand(rocks, sand, x_min, x_max, z_max, floor=True):
        if is_debug:
            log.debug("Grain %d", len(sand))
            debug_draw(rocks, sand, x_min, x_max, z_max)
        if (500, 0) in sand:
            break
    return len(sand)
