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


PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 4090701
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 6421


class Intcode:
    memory: list[int]
    pointer: int = 0

    def __init__(self, program: Iterable[int]):
        self.memory = list(program)

    def run(self) -> int:
        while (instruction := self.memory[self.pointer]) != 99:
            param_pointer = self.pointer + 1
            p1, p2, p3 = self.memory[param_pointer : param_pointer + 3]
            operand1 = self.memory[p1]
            operand2 = self.memory[p2]
            result = operand1 + operand2 if instruction == 1 else operand1 * operand2
            self.memory[p3] = result

            self.pointer += 4
        return self.memory[0]


def part_one(lines: Iterable[str]) -> int:
    program = [int(i) for i in "".join(lines).split(",")]
    program[1] = 12
    program[2] = 2
    ic = Intcode(program)
    return ic.run()


def part_two(lines: Iterable[str]) -> int:
    program = tuple(int(i) for i in "".join(lines).split(","))
    for noun, verb in itertools.product(range(100), range(100)):
        ic = Intcode(program)
        ic.memory[1] = noun
        ic.memory[2] = verb
        if ic.run() == 19690720:
            return 100 * noun + verb
    return -1
