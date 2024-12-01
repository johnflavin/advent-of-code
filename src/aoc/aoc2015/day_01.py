#!/usr/bin/env python
"""
PART 1
Read a sequence of ( and ).
Start at 0. ( means add one, ) means subtract 1.

PART 2
Find first character that causes sum to be negative. (1-indexed)
"""
from collections import Counter
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
))(((((
"""
PART_ONE_EXAMPLE_RESULT = 3
PART_ONE_RESULT = 280
PART_TWO_EXAMPLE = """\
()())
"""
PART_TWO_EXAMPLE_RESULT = 5
PART_TWO_RESULT = 1797


def part_one(lines: Iterable[str]) -> int:
    line = next(lines)
    counts = Counter(line)
    return counts.get("(", 0) - counts.get(")", 0)


def part_two(lines: Iterable[str]) -> int:
    line = next(lines)
    total = 0
    for i, ch in enumerate(line):
        total += 1 if ch == "(" else -1
        if total < 0:
            break
    return i + 1
