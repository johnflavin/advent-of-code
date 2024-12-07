#!/usr/bin/env python
"""
PART 1
Given lines of "test values" and space-separated ints,
distribute * and + operations (always evaluated left-to-right).
Sum all the test values that can possibly be made true.

PART 2
Add a concatenation operator.
"""

import logging
import operator
import re
from collections.abc import Iterable
from typing import Callable

PART_ONE_EXAMPLE = """\
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
"""
PART_ONE_EXAMPLE_RESULT = 3749
PART_ONE_RESULT = 2664460013123
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 11387
PART_TWO_RESULT = 426214131924213


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


type Op = Callable[[int, int], int]
OPS: tuple[Op, ...] = (operator.add, operator.mul)

LINE_RE = re.compile(r"(?P<test>\d+): (?P<values>(\d+ ?)+)")


def debug_log(test: int, actual: int, values: list[int], ops: Iterable[Op]) -> None:
    def op_str(op: Op) -> str:
        return "+" if op == operator.add else "*"

    s = [str(values[0])]
    for right, op in zip(values[1:], ops):
        s.extend((op_str(op), str(right)))
    s.extend(("=", str(actual), "==" if test == actual else "!=", str(test)))
    log.debug(" ".join(s))


def parse(line: str) -> tuple[int, list[int]]:
    if (m := LINE_RE.match(line)) is not None:
        test = int(m.group("test"))
        values = [int(val) for val in m.group("values").split()]
        return test, values
    raise ValueError(f'Can\'t parse line "{line}"')


def evaluate(left: int, values: list[int], next_right_idx: int) -> Iterable[int]:
    """Evaluate all operators on current left and next right"""
    return tuple(op(left, values[next_right_idx]) for op in OPS)


def find_all_possible_totals(values: list[int], ops: tuple[Op, ...]) -> list[int]:
    """Evaluate all possible combinations of operators between the values"""
    possible_totals = [values[0]]
    for right in values[1:]:
        possible_totals = [op(left, right) for left in possible_totals for op in ops]
    return possible_totals


def test_line(test: int, values: list[int], ops: tuple[Op, ...]) -> int:
    """Check all permutations of operators to see if the values can
    be made to equal the test value."""
    for actual in find_all_possible_totals(values, ops):
        if test == actual:
            return test
    return 0


def part_one(lines: Iterable[str]) -> int:
    ops: tuple[Op, ...] = (operator.add, operator.mul)
    return sum(test_line(*parse(line), ops) for line in lines if line)


def part_two(lines: Iterable[str]) -> int:
    def concat(left: int, right: int):
        return int(str(left) + str(right))

    ops: tuple[Op, ...] = (operator.add, operator.mul, concat)
    return sum(test_line(*parse(line), ops) for line in lines if line)
