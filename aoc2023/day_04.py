#!/usr/bin/env python
"""

PART 1
We have a list of numbers on cards.
On the left are "winning" numbers separated with pipes from a
list a numbers we "have".
Find out how many winning numbers we have on each card.
Wins are worth points. No wins is zero, n wins is 2^{n-1}.
Sum up the points in the cards.

PART 2
There are no points.
If a card gets n wins, we get another copy of the next n cards.
How many total cards do we play?
"""

from collections import Counter
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
"""
PART_ONE_EXAMPLE_RESULT = 13
PART_ONE_RESULT = 25174
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 30
PART_TWO_RESULT = 6420979


def parse(line: str) -> tuple[set[int], set[int]]:
    _, numbers = line.split(": ")
    winning_numbers, my_numbers = numbers.split(" | ")
    return set(int(num) for num in winning_numbers.split()), set(
        int(num) for num in my_numbers.split()
    )


def calculate_points(winning_numbers: set[int], my_numbers: set[int]) -> int:
    num_wins = calculate_number_of_wins(winning_numbers, my_numbers)
    return 0 if num_wins == 0 else 2 ** (num_wins - 1)


def calculate_number_of_wins(winning_numbers: set[int], my_numbers: set[int]) -> int:
    my_winning_numbers = my_numbers.intersection(winning_numbers)
    return len(my_winning_numbers)


def part_one(lines: Iterable[str]) -> int:
    return sum(calculate_points(*parse(line)) for line in lines if line)


def part_two(lines: Iterable[str]) -> int:
    multiplicities = Counter()
    for idx, line in enumerate(lines):
        multiplicity = multiplicities[idx]
        if multiplicity == 0:
            multiplicity = 1
            multiplicities[idx] = 1

        matches = calculate_number_of_wins(*parse(line))
        for next_card in range(idx, idx + matches):
            if next_card + 1 not in multiplicities:
                multiplicities[next_card + 1] = 1
            multiplicities[next_card + 1] += multiplicity

    return multiplicities.total()
