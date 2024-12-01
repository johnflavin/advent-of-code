#!/usr/bin/env python
"""
PART 1
Given two side-by-side lists of location ids,
sort both lists and take the absolute difference
between pairs.

PART 2
Calculate "similarity score"
For each item in the left list, count how often it is in the right list
and multiply those together. Total those.
"""
import logging
from collections.abc import Iterable
from collections import Counter


PART_ONE_EXAMPLE = """\
3   4
4   3
2   5
1   3
3   9
3   3
"""
PART_ONE_EXAMPLE_RESULT = 11
PART_ONE_RESULT = 2031679
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 31
PART_TWO_RESULT = 19678534


log = logging.getLogger(__name__)


def parse_lines(lines: Iterable[str]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return tuple(zip(*[tuple(int(n) for n in line.split()) for line in lines]))


def part_one(lines: Iterable[str]) -> int:
    lefts, rights = parse_lines(lines)
    lefts, rights = sorted(lefts), sorted(rights)
    return sum(abs(left - right) for left, right in zip(lefts, rights))


def part_two(lines: Iterable[str]) -> int:
    lefts, rights = parse_lines(lines)
    l_counts, r_counts = Counter(lefts), Counter(rights)
    return sum(
        left * l_count * r_counts.get(left, 0) for left, l_count in l_counts.items()
    )
