#!/usr/bin/env python
"""
PART 1
How many numbers meet some criteria?
They're in a given range, the digits are non-decreasing, and the
digits have at least one run of len two or more.

PART 2
Same rules as before, but digits must have a run of exactly two.
"""
import itertools
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 931
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 609


def get_digits(num: int) -> tuple[int, ...]:
    digits = []
    while num:
        div, rem = divmod(num, 10)
        digits.append(rem)
        num = div
    return tuple(reversed(digits))


def get_num(digits: tuple[int, ...]) -> int:
    num = 0
    for d in digits:
        num = num * 10 + d
    return num


def part_one(lines: Iterable[str]) -> int:

    def adjacent_digits_same(digits: tuple[int, ...]) -> bool:
        return any(d1 == d2 for d1, d2 in itertools.pairwise(digits))

    lower, upper = list(map(int, "".join(lines).split("-")))
    return sum(
        adjacent_digits_same((d0, d1, d2, d3, d4, d5))
        for d0 in range(lower // 100_000, upper // 100_000 + 1)
        for d1 in range(d0, 10)
        for d2 in range(d1, 10)
        for d3 in range(d2, 10)
        for d4 in range(d3, 10)
        for d5 in range(d4, 10)
        if lower <= get_num((d0, d1, d2, d3, d4, d5)) <= upper
    )


def part_two(lines: Iterable[str]) -> int:
    def at_least_one_run_of_len_two(digits: tuple[int, ...]) -> bool:
        # Left
        if digits[0] == digits[1] != digits[2]:
            return True
        # Right
        if digits[3] != digits[4] == digits[5]:
            return True
        # Middle
        for i in (1, 2, 3):
            if digits[i - 1] != digits[i] == digits[i + 1] != digits[i + 2]:
                return True
        return False

    lower, upper = list(map(int, "".join(lines).split("-")))
    return sum(
        at_least_one_run_of_len_two((d0, d1, d2, d3, d4, d5))
        for d0 in range(lower // 100_000, upper // 100_000 + 1)
        for d1 in range(d0, 10)
        for d2 in range(d1, 10)
        for d3 in range(d2, 10)
        for d4 in range(d3, 10)
        for d5 in range(d4, 10)
        if lower <= get_num((d0, d1, d2, d3, d4, d5)) <= upper
    )
