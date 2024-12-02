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
PART_TWO_RESULT = 553


log = logging.getLogger(__name__)


def parse(line: str) -> tuple[int, ...]:
    return tuple(map(int, line.split()))


def is_safe(line: Iterable[int]) -> bool:
    line = tuple(line)
    diffs = tuple(b - a for a, b in zip(line, line[1:]))
    sign = 1 if diffs[0] > 0 else -1
    for d in diffs:
        d_pos = d * sign
        if d_pos < 1 or d_pos > 3:
            return False
    return True


def is_safe_part_1(line: str) -> bool:
    return is_safe(parse(line))


def is_safe_part_2(line: str) -> bool:
    return any(
        is_safe(el for idx, el in enumerate(parse(line)) if idx != skip_idx)
        for skip_idx in range(len(line))
    )


def part_one(lines: Iterable[str]) -> int:
    return sum(map(is_safe_part_1, lines))


def part_two(lines: Iterable[str]) -> int:
    return sum(map(is_safe_part_2, lines))
