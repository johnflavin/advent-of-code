#!/usr/bin/env python
"""
PART 1
How many lines are "safe":
either monotonically increasing or decreasing
by at least 1 and at most 3"

PART 2
Same as part 1, except a line is "safe" if it would be considered "safe"
by dropping any one element.
"""
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9
"""
PART_ONE_EXAMPLE_RESULT = 2
PART_ONE_RESULT = 510
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 4
PART_TWO_RESULT = None


log = logging.getLogger(__name__)


def parse(line: str) -> tuple[int, ...]:
    return tuple(map(int, line.split()))


def take_diffs(line: Iterable[int]) -> tuple[int, ...]:
    return tuple(b - a for a, b in zip(line, line[1:]))


def in_range(test: int, low: int, high: int) -> bool:
    return low <= test <= high


def is_safe(diffs: tuple[int, ...]) -> bool:
    sign = 1 if diffs[0] > 0 else -1
    for d in diffs:
        d_pos = d * sign
        if d_pos < 0 or not in_range(d_pos, 1, 3):
            return False
    return True


def part_one(lines: Iterable[str]) -> int:
    return sum(is_safe(take_diffs(parse(line))) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    return sum(
        any(
            is_safe(take_diffs([el for idx, el in enumerate(parse(line)) if idx != i]))
            for i in range(len(line))
        )
        for line in lines
    )
