#!/usr/bin/env python
"""
PART 1
Given mass, find fuel as mass // 3 - 2
Sum fuel

PART 2
Add more fuel for mass of fuel
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
14
1969
100756
"""
PART_ONE_EXAMPLE_RESULT = 2 + 654 + 33583
PART_ONE_RESULT = 3287620
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 2 + 966 + 50346
PART_TWO_RESULT = 4928567


def calc_fuel(mass: int, recurse: bool) -> int:
    fuel_mass = (mass // 3) - 2
    if fuel_mass <= 0:
        return 0
    return fuel_mass + (calc_fuel(fuel_mass, recurse) if recurse else 0)


def part_one(lines: Iterable[str]) -> int:
    return sum(calc_fuel(int(line), False) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    return sum(calc_fuel(int(line), True) for line in lines)
