#!/usr/bin/env python
"""
PART 1
Total groups of numbers. Which group is greatest?

PART 2
Total groups of numbers. Sum top three.
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
1000
2000
3000

4000

5000
6000

7000
8000
9000

10000
"""
PART_ONE_EXAMPLE_RESULT = 24000
PART_ONE_RESULT = 69289
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 45000
PART_TWO_RESULT = 205615


def total_groups(lines: Iterable[str]) -> list[int]:
    totals = [0]
    for line in lines:
        if not line:
            totals.append(0)
            continue
        totals[-1] += int(line)
    return totals


def part_one(lines: Iterable[str]) -> int:
    totals = total_groups(lines)
    return max(totals)


def part_two(lines: Iterable[str]) -> int:
    totals = total_groups(lines)
    return sum(sorted(totals, reverse=True)[:3])
