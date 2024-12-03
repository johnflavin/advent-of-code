#!/usr/bin/env python
"""
PART 1
Given pairs of ranges, how many are completely contained in the other?

PART 2
Given pairs of ranges, how many overlap at all?
"""
from collections.abc import Iterable

from aoc.util import Range

PART_ONE_EXAMPLE = """\
2-4,6-8
2-3,4-5
5-7,7-9
2-8,3-7
6-6,4-6
2-6,4-8
"""
PART_ONE_EXAMPLE_RESULT = 2
PART_ONE_RESULT = 483
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 4
PART_TWO_RESULT = 874


def parse_line(line: str) -> list[Range]:
    range_str_pairs = line.split(",")
    return [
        Range(*list(map(int, range_strs.split("-")))) for range_strs in range_str_pairs
    ]


def any_contained(ranges: list[Range]) -> bool:
    return any(
        special_range in other_range
        for special_idx, special_range in enumerate(ranges)
        for other_idx, other_range in enumerate(ranges)
        if other_idx != special_idx
    )


def any_overlap(ranges: list[Range]) -> bool:
    return any(
        special_range.overlaps(other_range)
        for special_idx, special_range in enumerate(ranges)
        for other_idx, other_range in enumerate(ranges)
        if other_idx != special_idx
    )


def part_one(lines: Iterable[str]) -> int:
    return sum(any_contained(parse_line(line)) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    return sum(any_overlap(parse_line(line)) for line in lines)
