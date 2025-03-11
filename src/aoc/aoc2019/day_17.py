#!/usr/bin/env python
"""
PART 1
Run the intcode program.
It will output ASCII codes.
These can be interpreted as a camera view of a scene.
# for scaffold, . for empty, ^ v < or > for a robot.
Find all scaffold intersections and sum the products of their x and y.

PART 2
Need to come up with a sequence of moves to make a function (A, B, and C)
and a sequence of the functions.

Just visually inspecting the path and chunking it manually into segments

L,4,L,4,L,6,R,10,L,6
L,4,L,4,L,6,R,10,L,6
L,12,L,6,R,10,L,6
R,8,R,10,L,6,
R,8,R,10,L,6
L,4,L,4,L,6,R,10,L,6
R,8,R,10,L,6
L,12,L,6,R,10,L,6
R,8,R,10,L,6
L,12,L,6,R,10,L,6

A: L,4,L,4,L,6,R,10,L,6
B: L,12,L,6,R,10,L,6
C: R,8,R,10,L,6

A,A,B,C,C,A,C,B,C,B
"""
import logging
from collections.abc import Iterable

from aoc.util import add
from aoc.aoc2019.intcode import Intcode

PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 3448
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 762405


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


def part_one(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]
    ic = Intcode(program)
    ic.run()

    walls_or_robot = [ord(c) for c in ("#", "<", ">", "^", "v")]
    newline = ord("\n")

    wall_positions = set()
    y = 0
    x = 0
    dbg = ""
    for n in ic.outputs:
        if n == newline:
            y += 1
            x = 0

            if is_debug:
                log.debug(dbg)
                dbg = ""
            continue
        elif n in walls_or_robot:
            wall_positions.add((x, y))
            if is_debug:
                dbg += chr(n)
        elif is_debug:
            dbg += "."
        x += 1

    return sum(
        x * y
        for x, y in wall_positions
        if all(
            add((x, y), delta) in wall_positions
            for delta in ((0, 1), (1, 0), (-1, 0), (0, -1))
        )
    )


def part_two(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]

    # "wake the robot up"
    program[0] = 2
    ic = Intcode(program)

    # Setup
    ic.run()

    # inputs
    movement_sequence = "A,A,B,C,C,A,C,B,C,B\n"
    a = "L,4,L,4,L,6,R,10,L,6\n"
    b = "L,12,L,6,R,10,L,6\n"
    c = "R,8,R,10,L,6\n"
    camera = "n\n"
    for input_str in movement_sequence, a, b, c, camera:
        for c in input_str:
            ic.run(ord(c))

    return ic.outputs[-1]
