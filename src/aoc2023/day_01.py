#!/usr/bin/env python
"""
https://adventofcode.com/2023/day/1

part 1
Combine first and last digits in each line to make a single two-digit number,
then add all numbers

PART 2
Now the "digits" can be words
"""

from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T")


PART_ONE_EXAMPLE = """\
1abc2
pqr3stu8vwx
a1b2c3d4e5f
treb7uchet
"""
PART_ONE_EXAMPLE_RESULT = 142
PART_ONE_RESULT = 55477
PART_TWO_EXAMPLE = """\
two1nine
eightwothree
abcone2threexyz
xtwone3four
4nineeightseven2
zoneight234
7pqrstsixteen
"""
PART_TWO_EXAMPLE_RESULT = 281
PART_TWO_RESULT = 54431

ZERO_ORD = ord("0")

WORDS = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]


def char_to_digit(ch: str) -> int:
    """the digit represented by a one-character string, or -1"""
    possible_digit = ord(ch) - ZERO_ORD
    return possible_digit if 0 <= possible_digit <= 9 else -1


def line_to_digit_part1(line: str) -> int:
    first_digit = None
    last_digit = None
    for ch in line:
        digit = char_to_digit(ch)
        if digit > -1:
            # Found a digit
            first_digit = digit
            break
    for ch in reversed(line):
        digit = char_to_digit(ch)
        if digit > -1:
            last_digit = digit
            break
    return 10 * first_digit + last_digit


def line_to_digit_part2(line: str) -> int:
    first_letters = "zotfsen"
    digits = []
    pointer = 0
    while pointer < len(line):
        ch = line[pointer]
        if ch in "1234567890":
            digits.append(int(ch))
        elif ch in first_letters:
            digit = -1
            for word_idx, word in enumerate(WORDS):
                if line[pointer : pointer + len(word)] == word:
                    digit = word_idx
                    continue
            if digit > -1:
                digits.append(digit)

        pointer += 1
    return 10 * digits[0] + digits[-1]


def part_one(lines: Iterable[str]) -> int:
    return sum(map(line_to_digit_part1, lines))


def part_two(lines: Iterable[str]) -> int:
    return sum(map(line_to_digit_part2, lines))
