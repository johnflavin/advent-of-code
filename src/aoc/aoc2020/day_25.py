#!/usr/bin/env python
"""
PART 1
Find secrets given public keys

PART 2
N/A
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
5764801
17807724
"""
PART_ONE_EXAMPLE_RESULT = 14897079
PART_ONE_RESULT = 11288669
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None

MODULUS = 20201227
NOT_FOUND = -1


def part_one(lines: Iterable[str]) -> int:
    card_pk, door_pk = list(map(int, lines))

    subject_number = 7
    card_loop = NOT_FOUND
    door_loop = NOT_FOUND
    value = 1
    loop = 0
    while card_loop == NOT_FOUND or door_loop == NOT_FOUND:
        loop += 1
        value = (value * subject_number) % MODULUS
        if value == card_pk:
            card_loop = loop
        elif value == door_pk:
            door_loop = loop

    value = 1
    min_loop = min(card_loop, door_loop)
    other_pk = door_pk if min_loop == card_loop else card_pk
    for _ in range(min_loop):
        value = (value * other_pk) % MODULUS

    return value


def part_two(lines: Iterable[str]) -> int:
    return None
