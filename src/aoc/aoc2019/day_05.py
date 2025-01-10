#!/usr/bin/env python
"""
PART 1
Add opcodes 3 and 4 to store input and produce output, respectively.
Also add parameter modes.
Provide 1 as input.
Outputs should be all 0 except for last value, which is the answer.

PART 2
Implement opcodes 5, 6, 7, and 8
Provide 5 as an input and return the only output.
"""
from collections.abc import Iterable

from aoc.aoc2019.intcode import Intcode


PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 6745903
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 9168267


def part_one(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]
    ic = Intcode(program)
    ic.run(1)
    outputs = ic.outputs
    if any(o != 0 for o in outputs[:-1]):
        print("outputs should be 0:", outputs)
    return outputs[-1]


def part_two(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]
    ic = Intcode(program)
    ic.run(5)
    return ic.outputs[0]
