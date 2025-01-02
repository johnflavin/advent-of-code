#!/usr/bin/env python
"""
PART 1
Implement a formula evaluator with parens + left-to-right order of operations

PART 2
Now addition is higher precedence than multiplication
"""
import logging
import operator
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
1 + 2 * 3 + 4 * 5 + 6
1 + (2 * 3) + (4 * (5 + 6))
2 * 3 + (4 * 5)
5 + (8 * 3 + 9 + 3 * 4 * 3)
5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))
((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2
"""
PART_ONE_EXAMPLE_RESULT = 71 + 51 + 26 + 437 + 12240 + 13632
PART_ONE_RESULT = 25190263477788
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 231 + 51 + 46 + 1445 + 669060 + 23340
PART_TWO_RESULT = 297139939002972

log = logging.getLogger(__name__)

OPS = {
    "+": operator.add,
    "*": operator.mul,
}
type Stack = list[int | str]


def reduce_once(stack: Stack) -> None:
    right = stack.pop()
    op = stack.pop()
    left = stack.pop()
    log.debug("%d %s %d", left, op, right)
    stack.append(OPS[op](left, right))


def reduce(stack: Stack) -> int:
    while len(stack) > 1:
        reduce_once(stack)
    return stack[0]


def evaluate(line: str, part1: bool) -> int:
    stacks = [[]]
    for cs in line.split():
        for c in cs:
            if c == "(":
                stacks.append([])
            elif c == ")":
                top = stacks.pop()
                stacks[-1].append(reduce(top))
            elif 0 <= (i := ord(c) - 48) <= 9:
                stacks[-1].append(i)
            else:
                stacks[-1].append(c)

            if len(stacks[-1]) >= 3 and (part1 or stacks[-1][-2] == "+"):
                reduce_once(stacks[-1])

    return reduce(stacks[-1])


def part_one(lines: Iterable[str]) -> int:
    return sum(evaluate(line, True) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    return sum(evaluate(line, False) for line in lines)
