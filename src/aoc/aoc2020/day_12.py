#!/usr/bin/env python
"""
PART 1
We have a position and a heading (degrees, probably only multiples of 90)
Follow directions and determine manhattan distance from start.

PART 2
Now we only move the ship on F instructions.
"heading" is more of a vector, starts at (10, -1).
NSEW move the heading instead of the ship.
"""
import logging
from collections.abc import Iterable

from aoc.util import Coord, add

PART_ONE_EXAMPLE = """\
F10
N3
F7
R90
F11
"""
PART_ONE_EXAMPLE_RESULT = 25
PART_ONE_RESULT = 796
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 286
PART_TWO_RESULT = 39446

log = logging.getLogger(__name__)


type Instruction = tuple[str, int]

DIRECTIONS = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}


def parse(lines: Iterable[str]) -> Iterable[Instruction]:
    for line in lines:
        yield line[0], int(line[1:])


def rotate(heading: Coord, direction: str, units: int) -> Coord:
    if units == 0:
        return heading
    elif units == 180:
        return -heading[0], -heading[1]
    elif (direction == "R" and units == 90) or (direction == "L" and units == 270):
        return -heading[1], heading[0]
    elif (direction == "R" and units == 270) or (direction == "L" and units == 90):
        return heading[1], -heading[0]
    else:
        raise ValueError("Don't know how to rotate %s%d", direction, units)


def move(
    pos: Coord, heading: Coord, direction: str, units: int, part1: bool = True
) -> tuple[Coord, Coord]:
    delta = heading if direction == "F" else DIRECTIONS[direction]
    if part1 or direction == "F":
        return add(pos, (units * delta[0], units * delta[1])), heading
    else:
        return pos, add(heading, (units * delta[0], units * delta[1]))


def run_instructions(
    lines: Iterable[str], pos: Coord, heading: Coord, part1: bool = True
) -> int:
    log.debug("Start: pos=%s heading=%s", pos, heading)
    for direction, units in parse(lines):
        if direction in "RL":
            log.debug("Rorate %s%d", direction, units)
            heading = rotate(heading, direction, units)
        else:
            log.debug("Move %s%d", direction, units)
            pos, heading = move(pos, heading, direction, units, part1)
        log.debug("pos=%s heading=%s", pos, heading)
    return abs(pos[0]) + abs(pos[1])


def part_one(lines: Iterable[str]) -> int:
    return run_instructions(lines, (0, 0), DIRECTIONS["E"], part1=True)


def part_two(lines: Iterable[str]) -> int:
    return run_instructions(lines, (0, 0), (10, -1), part1=False)
