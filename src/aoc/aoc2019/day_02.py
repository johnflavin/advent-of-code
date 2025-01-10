#!/usr/bin/env python
"""
PART 1
Implement an intcode computer according to some instructions.
Replace the input of the program with value 12 at pos. 1 and 2 at 2.
What value is at position 0?

PART 2
Find the values that need to go in positions 1 and 2 (between 0 and 99 incl.)
that produces the value 19690720 in position 0.
"""
import itertools
from collections.abc import Iterable

from aoc.aoc2019.intcode import Intcode


PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 4090701
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 6421


def part_one(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]
    ic = Intcode(program)
    ic.mem[1] = 12
    ic.mem[2] = 2
    ic.run()
    return ic.mem[0]


def part_two(lines: Iterable[str]) -> int:
    program = tuple(int(i) for i in "".join(lines).split(","))
    for noun, verb in itertools.product(range(100), range(100)):
        ic = Intcode(program)
        ic.mem[1] = noun
        ic.mem[2] = verb
        ic.run()
        if ic.mem[0] == 19690720:
            return 100 * noun + verb
    return -1
