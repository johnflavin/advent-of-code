#!/usr/bin/env python
"""
PART 1
For groups of lines, count number of unique chars, then sum group counts

PART 2
Only count chars that are in every line in the group
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
abc

a
b
c

ab
ac

a
a
a
a

b
"""
PART_ONE_EXAMPLE_RESULT = 11
PART_ONE_RESULT = 6291
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 6
PART_TWO_RESULT = 3052


def part_one(lines: Iterable[str]) -> int:
    total = 0
    group = set()
    for line in lines:
        if line == "":
            total += len(group)
            group = set()
        else:
            group.update(line)
    total += len(group)
    return total


def part_two(lines: Iterable[str]) -> int:
    total = 0
    group = set()
    newgroup = True
    for line in lines:
        if line == "":
            total += len(group)
            group = set()
            newgroup = True
        elif newgroup:
            newgroup = False
            group.update(line)
        else:
            group.intersection_update(set(line))
    total += len(group)
    return total
