#!/usr/bin/env python
"""
PART 1
Given a grid of solid objects (#) and a starting
location + direction (^), walk forward until reaching
a solid object, then turn right. How many spaces
do you visit before leaving the area?

PART 2
How many positions could you add an obstacle to cause the path to loop?
"""
import logging
from collections.abc import Iterable

from aoc.util import Pt


PART_ONE_EXAMPLE = """\
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
"""
PART_ONE_EXAMPLE_RESULT = 41
PART_ONE_RESULT = 5131
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 6
PART_TWO_RESULT = 1784


log = logging.getLogger(__name__)


def add(a: Pt, b: Pt) -> Pt:
    return a[0] + b[0], a[1] + b[1]


def turn_right(forward: Pt) -> Pt:
    """Rotate a direction vector (one axis = 0, the other ±1)
    to the right.

    Note that pos (neg) x is right (left) and pos (neg) y is down (up)"""
    #  1,  0 right ->  0,  1  down
    # -1,  0  left ->  0, -1    up
    #  0, -1    up ->  1,  0 right
    #  0,  1  down -> -1,  0  left
    x, y = forward
    return -y, x


def step(pos: Pt, facing: Pt, obstacles: set[Pt]) -> tuple[Pt, Pt]:
    """Step forward unless you hit an obstacle, then turn right
    and try again up to a total of three times. (because four tries is a circle)
    Return the next pos, forward pair."""
    for turn in range(3):
        # Don't turn on the first iteration, but do turn after that
        facing = turn_right(facing) if turn else facing
        # Try stepping from current position in the direction we are facing
        step_forward = add(pos, facing)
        # If you hit an obstacle try again
        if step_forward in obstacles:
            continue
        # Didn't hit an obstacle, valid step
        return step_forward, facing
    raise Exception("We're stuck")


def read_grid(lines: Iterable[str]) -> tuple[Pt, Pt, set[Pt], int, int]:
    """Read the input grid. Return starting position and facing direction,
    a set of obstacle locations, and the max x and y values."""
    start: Pt = (-1, -1)
    facing: Pt = (0, 0)
    obstacles = set()
    max_y = 0
    x = 0

    for y, line in enumerate(lines):
        if not line:
            continue
        max_y = y
        for x, ch in enumerate(line):
            if ch == "#":
                obstacles.add((x, y))
            elif ch in "^v<>":
                start = (x, y)
                facing = (
                    0 if ch in "^v" else 1 if ch == ">" else -1,
                    0 if ch in "<>" else 1 if ch == "v" else -1,
                )
    return start, facing, obstacles, x + 1, max_y + 1


def walk(pos, facing, obstacles, max_x, max_y) -> tuple[set[tuple[Pt, Pt]], bool]:
    history = set()
    while 0 <= pos[0] < max_x and 0 <= pos[1] < max_y and (pos, facing) not in history:
        # Record that we were here
        history.add((pos, facing))

        # Take the next valid step
        pos, facing = step(pos, facing, obstacles)
    return history, (pos, facing) in history


def part_one(lines: Iterable[str]) -> int:
    start, facing, obstacles, max_x, max_y = read_grid(lines)

    # Walk the route, recording where we have been
    history, _ = walk(start, facing, obstacles, max_x, max_y)

    # History gives us the pos, facing pairs, but we only care about pos
    locations_visited = {pos for pos, _ in history}

    if log.isEnabledFor(logging.DEBUG):
        log.debug("Locations visited (not in order):")
        for pos in sorted(locations_visited):
            log.debug("%s", pos)

    return len(locations_visited)


def part_two(lines: Iterable[str]) -> int:
    start, facing, obstacles, max_x, max_y = read_grid(lines)
    log.debug("max_x=%d, max_y=%d", max_x, max_y)

    # Walk the route without any alterations, to find valid new obstacle locations
    history, _ = walk(start, facing, obstacles, max_x, max_y)
    locations_visited = {pos for pos, _ in history}

    return sum(
        walk(start, facing, {*obstacles, ob}, max_x, max_y)[1]
        for ob in locations_visited
    )
