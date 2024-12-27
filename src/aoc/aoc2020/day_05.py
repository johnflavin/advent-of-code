#!/usr/bin/env python
"""
PART 1
Take a "seat assignment" as a binary number.
Find the max.

PART 2
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
FBFBBFFRLR
BFFFBBFRRR
FFFBBBFRRR
BBFFBBFRLL
"""
PART_ONE_EXAMPLE_RESULT = 820
PART_ONE_RESULT = 871
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 640


def seat_int(seat: str) -> int:
    return sum((c == "B" or c == "R") << i for i, c in enumerate(reversed(seat)))


def part_one(lines: Iterable[str]) -> int:
    return max(map(seat_int, lines))


def part_two(lines: Iterable[str]) -> int:
    occupied = set(map(seat_int, lines))
    all_seats = set(range(1 << 11))
    unoccupied = all_seats - occupied
    for uo in unoccupied:
        if (uo - 1) in occupied and (uo + 1) in occupied:
            return uo
    return -1
