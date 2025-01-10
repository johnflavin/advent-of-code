#!/usr/bin/env python
"""
PART 1
Wire several intcode programs together, outputs to inputs.
Now the program has to be capable of stopping and waiting for an input.
Feed one input to each program from a "phase sequence" permutation of 01234,
then feed 0 to the first program and its output to the next input, etc.
Find the phase sequence that maximizes the final output.

PART 2
Hook the output of the last amplifier back into the first and run until they stop.
Find max output for all phase sequences (perms. of 56789).
"""
import itertools
from collections.abc import Iterable

from aoc.aoc2019.intcode import run_amplifiers


PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 22012
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 4039164


def part_one(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]

    return max(
        run_amplifiers(program, seq, False) for seq in itertools.permutations(range(5))
    )


def part_two(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]

    return max(
        run_amplifiers(program, seq, True)
        for seq in itertools.permutations(range(5, 10))
    )
