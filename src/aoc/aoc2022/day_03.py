#!/usr/bin/env python
"""
PART 1
Find a letter that appears in both the first half and second
half of each line.
Score as a=1, b=2, ..., z=26, A=27, ..., Z=52

PART 2
Find a letter in common among groups of three consecutive lines (no reuse)
Score as before
"""
import itertools
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
ttgJtRGJQctTZtZT
CrZsJsPPZsGzwwsLwLmpwMDw
"""
PART_ONE_EXAMPLE_RESULT = 157
PART_ONE_RESULT = 8018
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 70
PART_TWO_RESULT = 2518

ORD_LOWER_A = ord("a")
ORD_UPPER_A = ord("A")


def score(letter: str) -> int:
    o = ord(letter)
    return o - (ORD_LOWER_A if o >= ORD_LOWER_A else ORD_UPPER_A - 26) + 1


def part_one(lines: Iterable[str]) -> int:

    def find_letter(line: str) -> str:
        midpoint = len(line) // 2
        return set(line[:midpoint]).intersection(set(line[midpoint:])).pop()

    return sum(score(find_letter(line)) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    def find_letter(line_group: tuple[str, str, str]) -> str:
        sets = list(map(set, line_group))
        letter = sets[0].intersection(sets[1]).intersection(sets[2]).pop()
        logging.debug("---")
        logging.debug(line_group[0])
        logging.debug(line_group[1])
        logging.debug(line_group[2])
        logging.debug(letter)
        return letter

    return sum(
        score(find_letter(line_group)) for line_group in itertools.batched(lines, 3)
    )
