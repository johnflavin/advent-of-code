#!/usr/bin/env python
"""
PART 1
Given a list of present box dimensions lxwxh
For each present calculate area of paper to cover it.
Surface area: 2*l*w + 2*w*h + 2*h*l
Plus a little slack: area of smallest side
Sum areas

PART 2
Calculate length of ribbon required.
= Perimeter of shortest side (l + w, say)
  + volume of box (l*w*h)
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
2x3x4
1x1x10
"""
PART_ONE_EXAMPLE_RESULT = 101
PART_ONE_RESULT = 1586300
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 48
PART_TWO_RESULT = None


def parse(line: str) -> tuple[int, int, int]:
    return tuple(map(int, line.split("x", 3)))


def calc_paper_area(length: int, width: int, height: int) -> int:
    surface_area = 2 * (length * width + width * height + length * height)
    smallest_side_dims = sorted([length, width, height])
    slack = smallest_side_dims[0] * smallest_side_dims[1]
    return surface_area + slack


def calc_ribbon_length(length: int, width: int, height: int) -> int:
    smallest_side_dims = sorted([length, width, height])
    perimeter = 2 * (smallest_side_dims[0] + smallest_side_dims[1])
    bow = length * width * height
    return perimeter + bow


def part_one(lines: Iterable[str]) -> int:
    return sum(calc_paper_area(*parse(line)) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    return sum(calc_ribbon_length(*parse(line)) for line in lines)
