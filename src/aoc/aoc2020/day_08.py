#!/usr/bin/env python
"""
PART 1
Follow operations until they loop, return value of accumulator

PART 2
Change one nop to jmp or jmp to nop so the program terminates.
Return value of accumulator.
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
nop +0
acc +1
jmp +4
acc +3
jmp -3
acc -99
acc +1
jmp -4
acc +6
"""
PART_ONE_EXAMPLE_RESULT = 5
PART_ONE_RESULT = 1521
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 8
PART_TWO_RESULT = 1016


type Instruction = tuple[str, int]


def parse(line: str) -> Instruction:
    op, value_str = line.split(" ")
    return op, int(value_str)


def execute(instructions: tuple[Instruction, ...]) -> tuple[bool, int]:
    li = len(instructions)
    executed = set()
    i = 0
    a = 0
    while i not in executed and i < li:
        executed.add(i)
        op, value = instructions[i]
        if op == "jmp":
            i += value
            continue
        elif op == "acc":
            a += value
        i += 1
    return i == li, a


def part_one(lines: Iterable[str]) -> int:
    instructions = tuple(map(parse, lines))
    _, a = execute(instructions)
    return a


def part_two(lines: Iterable[str]) -> int:
    instructions = tuple(map(parse, lines))
    for i, (inst, val) in enumerate(instructions):
        if inst == "acc":
            continue
        test_inst = "jmp" if inst == "nop" else "nop"
        test_instructions = (
            *instructions[:i],
            (test_inst, val),
            *instructions[i + 1 :],
        )
        did_complete, a = execute(test_instructions)
        if did_complete:
            return a
    return -1
