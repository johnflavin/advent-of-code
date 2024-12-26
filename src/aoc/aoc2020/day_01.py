#!/usr/bin/env python
"""
PART 1
Find two numbers that add to 2020, then multiply them.

PART 2
Find three numbers that add to 2020, then multiple them.
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
1721
979
366
299
675
1456
"""
PART_ONE_EXAMPLE_RESULT = 514579
PART_ONE_RESULT = 567171
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 241861950
PART_TWO_RESULT = 212428694


def part_one(lines: Iterable[str]) -> int:
    looking_for = set()
    for line in lines:
        n = int(line)
        m = 2020 - n
        if m in looking_for:
            return n * m
        looking_for.add(n)
    return -1


def part_two(lines: Iterable[str]) -> int:
    looking_for = {}
    for line in lines:
        a = int(line)
        diff = 2020 - a
        for b, possible_answers in looking_for.items():
            c = diff - b
            if c in possible_answers:
                return a * b * c
            looking_for[b].add(a)
        looking_for[a] = set()

    return -1
