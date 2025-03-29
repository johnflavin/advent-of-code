#!/usr/bin/env python
"""
PART 1
Run an intcode program for input x,y coords in the range 0–49,0–49

PART 2
Find the lowest top-left corner of a 100x100 square that fits entirely within
the beam
"""
import logging
from collections.abc import Iterable

from aoc.aoc2019.intcode import Intcode


PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 118
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 18651593

log = logging.getLogger(__name__)


def part_one(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]

    def test(x: int, y: int) -> int:
        ic = Intcode(program)
        ic.run(x)
        ic.run(y)
        return ic.outputs[0]

    size = 50

    edges = {0: (0, 0)}
    xmin, xmax, y = 6, 6, 5
    while True:

        if y >= size:
            break

        # Find left edge
        while test(xmin, y) == 0:
            xmin += 1

        # Find right edge
        xmax += 1
        while xmax < size and test(xmax, y) == 1:
            xmax += 1
        xmax -= 1

        edges[y] = (xmin, xmax)

        y += 1

    total = 0
    for y in range(size):
        xmin, xmax = edges.get(y, (-1, -1))
        log.info("".join("#" if xmin <= x <= xmax else "." for x in range(size)))
        total += sum(1 for x in range(size) if xmin <= x <= xmax)

    return total


def part_two(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]

    def test(x: int, y: int) -> int:
        ic = Intcode(program)
        ic.run(x)
        ic.run(y)
        return ic.outputs[0]

    size = 100
    x, y = 6, 5
    while True:

        # Find next left edge (x, y)
        while test(x, y) == 0:
            x += 1

        # Check if we can make a square
        y_sq = y - (size - 1)
        if test(x + size - 1, y_sq) == 1:
            # log.info("Found square: (%d, %d)", x, y_sq)
            return 10_000 * x + y_sq

        y += 1
