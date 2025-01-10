#!/usr/bin/env python
"""
PART 1
Implement relative param mode and opcode 9.
Run intcode program with input 1.
If anything is wrong it will output the opcodes that failed,
otherwise it will output a single value (the answer)

PART 2
Run with input 2, answer is single output.
"""
from collections.abc import Iterable

from aoc.aoc2019.intcode import Intcode


PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 3454977209
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 50120


def part_one(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]
    ic = Intcode(program)
    ic.run(1)
    if len(ic.outputs) == 1:
        return ic.outputs[0]
    print(ic.outputs)
    return -1


def part_two(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]
    ic = Intcode(program)
    ic.run(2)
    if len(ic.outputs) == 1:
        return ic.outputs[0]
    print(ic.outputs)
    return -1
