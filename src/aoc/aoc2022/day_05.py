#!/usr/bin/env python
"""
PART 1
Given a starting set of crates in stacks and a procedure for moving them,
find which crates end up at the top of the stacks.
An instruction which moves more than one goes one at a time,
which results in flipping the substack upon move.

PART 2
Given a starting set of crates in stacks and a procedure for moving them,
find which crates end up at the top of the stacks.
An instruction which moves more than one goes all at once,
which results in not flipping the substack upon move.
"""

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass

PART_ONE_EXAMPLE = """\
    [D]    
[N] [C]    
[Z] [M] [P]
 1   2   3 

move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2
"""  # noqa: W291
PART_ONE_EXAMPLE_RESULT = "CMZ"
PART_ONE_RESULT = "FJSRQCFTN"
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = "MCD"
PART_TWO_RESULT = "CJVLJQPHS"


log = logging.getLogger(__name__)


INSTRUCTION_RE = re.compile(r"move (?P<num>\d+) from (?P<source>\d+) to (?P<dest>\d+)")


@dataclass(frozen=True)
class Instruction:
    number: int
    source: str
    dest: str


type Stack = list[str]
type Stacks = dict[str, Stack]


def debug_log_stacks(stacks: Stacks) -> None:
    for stack_label_char, stack in stacks.items():
        log.debug("Stack %s: %s", stack_label_char, stack)


def parse_input(lines: Iterable[str]) -> tuple[Stacks, list[Instruction]]:
    """First n lines are the contents of the stacks (top to bottom).
    When we reach a line of numbers, that tells us how many stacks there are.
    Following a blank line the instructions begin (first to last)."""
    log.debug("Loading stacks")
    lines = iter(lines)
    stack_contents_lines = []
    while line := next(lines):
        log.debug(line)
        stack_contents_lines.append(line)
    stack_label_line = stack_contents_lines.pop()
    stacks = {}
    for stack_label_idx, stack_label_char in enumerate(stack_label_line):
        if stack_label_char == " ":
            # whitespace, not a label
            continue
        # Create a new empty stack
        stacks[stack_label_char] = []

        # Go through lines of stack contents, pulling out whatever is at this
        #  same index
        for stack_contents in stack_contents_lines:
            try:
                stack_char = stack_contents[stack_label_idx]
            except IndexError:
                stack_char = " "
            if stack_char != " ":
                stacks[stack_label_char].insert(0, stack_char)
    if log.isEnabledFor(logging.DEBUG):
        debug_log_stacks(stacks)

    instructions = [
        Instruction(int(m.group("num")), m.group("source"), m.group("dest"))
        for line in lines
        if (m := INSTRUCTION_RE.match(line))
    ]
    log.debug("Instructions %s", instructions)

    return stacks, instructions


def part_one(lines: Iterable[str]) -> str:
    stacks, instructions = parse_input(lines)

    for instruction in instructions:
        for _ in range(instruction.number):
            stacks[instruction.dest].append(stacks[instruction.source].pop())
        if log.isEnabledFor(logging.DEBUG):
            log.debug(instruction)
            debug_log_stacks(stacks)

    return "".join(stack.pop() for stack in stacks.values())


def part_two(lines: Iterable[str]) -> str:
    stacks, instructions = parse_input(lines)

    for instruction in instructions:
        stacks[instruction.dest].extend(
            stacks[instruction.source][-instruction.number :]
        )
        stacks[instruction.source] = stacks[instruction.source][: -instruction.number]
        if log.isEnabledFor(logging.DEBUG):
            log.debug(instruction)
            debug_log_stacks(stacks)

    return "".join(stack.pop() for stack in stacks.values())
