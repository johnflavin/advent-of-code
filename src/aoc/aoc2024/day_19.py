#!/usr/bin/env python
"""
PART 1
Find arrangements of color sequences.
First part is simply counting which are possible.

PART 2
Sum all possible sequences
"""
from collections.abc import Iterable
from functools import cache

PART_ONE_EXAMPLE = """\
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb
"""
PART_ONE_EXAMPLE_RESULT = 6
PART_ONE_RESULT = 360
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 16
PART_TWO_RESULT = 577474410989846


def part_one(lines: Iterable[str]) -> int:
    lines = iter(lines)
    available = set(next(lines).split(", "))
    max_len_available = max(map(len, available))

    next(lines)  # Blank

    @cache
    def is_possible(design: str) -> bool:
        ld = len(design)
        if ld == 1:
            result = design in available
        elif ld <= max_len_available and design in available:
            result = True
        else:
            result = any(
                design[: split_idx + 1] in available
                and is_possible(design[split_idx + 1 :])
                for split_idx in range(len(design))
            )
        return result

    return sum(is_possible(design_str) for design_str in lines)


def part_two(lines: Iterable[str]) -> int:
    lines = iter(lines)
    available = set(next(lines).split(", "))

    next(lines)  # Blank

    @cache
    def num_possible(design: str) -> int:
        ld = len(design)
        if ld == 0:
            # I don't know if this will come up but just in case
            return 1
        elif ld == 1:
            result = int(design in available)
        else:
            result = sum(
                (
                    num_possible(design[split_idx + 1 :])
                    if design[: split_idx + 1] in available
                    else 0
                )
                for split_idx in range(len(design))
            )
        return result

    return sum(num_possible(design_str) for design_str in lines)
