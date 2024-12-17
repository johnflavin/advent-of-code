#!/usr/bin/env python
"""
PART 1
It's a program with registers and operations.
I'm not summarizing it because it is a lot.

PART 2
Run the program with register A set to successive ints
until the program outputs itself.

...do we have to solve the halting problem?

I don't think I would have come up with this on my own, but
I looked at Reddit and came up with an idea.
Looks like we build A digit-by-digit (base 8).
Starting from the LSD, we run the program until it matches the last
digit of the program.
Then we move to the next, match the next, and so on.
"""

import logging
import re
from collections import deque
from collections.abc import Iterable
from typing import Callable

PART_ONE_EXAMPLE = """\
Register A: 729
Register B: 0
Register C: 0

Program: 0,1,5,4,3,0
"""
PART_ONE_EXAMPLE_RESULT = "4,6,3,5,6,3,5,2,1,0"
PART_ONE_RESULT = "1,5,0,3,7,3,0,3,1"
PART_TWO_EXAMPLE = """\
Register A: 2024
Register B: 0
Register C: 0

Program: 0,3,5,4,3,0
"""
PART_TWO_EXAMPLE_RESULT = 117440
PART_TWO_RESULT = 105981155568026

log = logging.getLogger(__name__)

type oint = int | None
type InstructionResult = tuple[oint, oint]

REGISTER_RE = re.compile(r"Register (?P<name>[ABC]): (?P<value>\d+)")


def parse_register(line: str) -> tuple[str, int]:
    if (m := REGISTER_RE.match(line)) is not None:
        return m.group("name"), int(m.group("value"))


def run(program: Iterable[int], **registers) -> Iterable[int]:
    def resolve_combo_operand(combo_operand: int) -> oint:
        if combo_operand <= 3:
            return combo_operand
        elif combo_operand < 7:
            # 4 + 61 = 65 -> A
            # 5 + 61 = 66 -> B
            # 6 + 61 = 67 -> C
            return registers[chr(combo_operand + 61)]

    def dv(register: str, combo_operand: int) -> InstructionResult:
        operand = resolve_combo_operand(combo_operand)
        registers[register] = registers["A"] >> operand
        return None, None

    def adv(combo_operand: int) -> InstructionResult:
        return dv("A", combo_operand)

    def bxl(operand: int) -> InstructionResult:
        registers["B"] = registers["B"] ^ operand
        return None, None

    def bst(combo_operand: int) -> InstructionResult:
        operand = resolve_combo_operand(combo_operand)
        registers["B"] = operand & 0b111
        return None, None

    def jnz(operand: int) -> InstructionResult:
        if registers["A"] == 0:
            return None, None
        return operand, None

    def bxc(_: int) -> InstructionResult:
        registers["B"] = registers["B"] ^ registers["C"]
        return None, None

    def out(combo_operand: int) -> InstructionResult:
        operand = resolve_combo_operand(combo_operand)
        return None, operand & 0b111

    def bdv(combo_operand: int) -> InstructionResult:
        return dv("B", combo_operand)

    def cdv(combo_operand: int) -> InstructionResult:
        return dv("C", combo_operand)

    instructions: tuple[Callable[[int], InstructionResult]] = (
        adv,
        bxl,
        bst,
        jnz,
        bxc,
        out,
        bdv,
        cdv,
    )
    program = tuple(program)
    num_instructions = len(program)
    pointer = 0
    # log.debug(
    #     "pointer=%d A=%d B=%d C=%d",
    #     pointer,
    #     registers["A"],
    #     registers["B"],
    #     registers["C"],
    # )
    while pointer < num_instructions:
        opcode = program[pointer]
        pointer += 1
        operand = program[pointer]
        pointer += 1
        # log.debug("opcode=%d operand=%d", opcode, operand)
        instruction = instructions[opcode]
        result_pointer, result_out = instruction(operand)
        # log.debug("instruction=%s(%d), result=(%s, %s)",
        #           instruction.__name__, operand, result_pointer, result_out)
        if result_pointer is not None:
            # log.debug("jump %d", result_pointer)
            pointer = result_pointer
        if result_out is not None:
            # log.debug("yield %d", result_out)
            yield result_out
        # log.debug(
        #     "pointer=%d A=%d B=%d C=%d",
        #     pointer,
        #     registers["A"],
        #     registers["B"],
        #     registers["C"],
        # )


def part_one(lines: Iterable[str]) -> str:
    lines = list(lines)
    registers = dict(map(parse_register, lines[:3]))
    program = list(map(int, lines[4].split()[1].split(",")))

    return ",".join(map(str, run(program, **registers)))


def part_two(lines: Iterable[str]) -> int:
    lines = list(lines)
    registers = dict(map(parse_register, lines[:3]))
    program = list(map(int, lines[4].split()[1].split(",")))
    b = registers["B"]
    c = registers["C"]

    # kernels: (kernel, num octal digits in kernel)
    kernels = deque([(0, 0)])

    while kernels:
        kernel, k_size = kernels.popleft()
        shifted_kernel = kernel << 3
        a_size = k_size + 1
        for i in range(8):
            a = shifted_kernel + i

            output = list(run(program, A=a, B=b, C=c))

            if output == program:
                log.debug("A=%s", oct(a))
                log.debug(" OUT=%s", ".".join(map(str, output[-a_size:])))
                log.debug("PROG=%s", ".".join(map(str, program[-a_size:])))
                log.debug("SUCCESS")
                # There may be other inputs that match, but given how
                #  we iterate though them we will find the lowest first
                return a
            elif output[-a_size:] == program[-a_size:]:
                log.debug("A=%s", oct(a))
                log.debug(" OUT[-%d:]=%s", a_size, ".".join(map(str, output[-a_size:])))
                log.debug(
                    "PROG[-%d:]=%s", a_size, ".".join(map(str, program[-a_size:]))
                )
                kernels.append((a, a_size))

    return -1
