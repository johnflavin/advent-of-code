#!/usr/bin/env python
"""
PART 1
Use intcode program to build a painting robot.
It moves on a 2d grid, all squares initially painted black (0).
While the program runs...
Feed the input the value of the current square: black=0 white=1
It will output two numbers: 0 or 1 to paint current square, and
0 or 1 to turn left or right. Then it moves one forward.
For part 1 we need only count how many squares get painted,
i.e. how many steps the program runs.

PART 2
Feed the input a 1 to start. Print the output.
"""
from collections import defaultdict
from collections.abc import Iterable

from aoc.util import Pt, add
from aoc.aoc2019.intcode import Intcode

PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 1681
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = """
⬛️⬜️⬜️⬜️⬜️⬛️⬛️⬜️⬜️⬛️⬛️⬜️⬜️⬜️⬜️⬛️⬛️⬜️⬜️⬛️⬛️⬜️⬜️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬛️⬛️
⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬜️⬛️⬛️⬛️⬛️
⬛️⬜️⬜️⬜️⬛️⬛️⬜️⬛️⬛️⬛️⬛️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬜️⬛️⬛️⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬜️⬛️⬛️⬛️⬛️⬛️
⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬜️⬜️⬛️⬛️⬜️⬛️⬛️⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬜️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬜️⬛️⬜️⬛️⬜️⬛️⬛️⬛️⬛️
⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬜️⬛️⬛️⬛️⬛️
⬛️⬜️⬜️⬜️⬜️⬛️⬛️⬜️⬜️⬜️⬛️⬜️⬜️⬜️⬜️⬛️⬛️⬜️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬜️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬛️⬛️
"""


COLOR = {0: "⬛️", 1: "⬜️"}


def rotate_right(pt: Pt) -> Pt:
    return -pt[1], pt[0]


def rotate_left(pt: Pt) -> Pt:
    return pt[1], -pt[0]


def run_program(ic: Intcode, starting_value: int) -> dict[Pt, int]:
    pt = (0, 0)
    heading = (0, -1)
    squares = defaultdict(int)
    squares[pt] = starting_value
    while not ic.is_halted:
        # Feed current value as input
        ic.run(squares[pt])

        # Get outputs
        paint_output, turn_output = ic.outputs[-2:]

        # Paint current square
        squares[pt] = paint_output

        # Turn
        heading = (rotate_right if turn_output else rotate_left)(heading)

        # Move
        pt = add(pt, heading)

    return squares


def part_one(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]
    ic = Intcode(program)
    squares = run_program(ic, 0)
    return len(squares)


def part_two(lines: Iterable[str]) -> str:
    program = [int(i) for i in "".join(lines).split(",")]
    ic = Intcode(program)
    squares = run_program(ic, 1)

    # Print the output
    x_bounds = [0, 0]
    y_bounds = [0, 0]
    for x, y in squares:
        if x > x_bounds[1]:
            x_bounds[1] = x
        elif x < x_bounds[0]:
            x_bounds[0] = x
        if y > y_bounds[1]:
            y_bounds[1] = y
        elif y < y_bounds[0]:
            y_bounds[0] = y

    return (
        "\n"
        + "\n".join(
            "".join(COLOR[squares[(x, y)]] for x in range(x_bounds[0], x_bounds[1] + 1))
            for y in range(y_bounds[0], y_bounds[1] + 1)
        )
        + "\n"
    )
