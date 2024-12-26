#!/usr/bin/env python
"""
PART 1
Lines specify a range of times a char must appear and a string.
Count strings that obey the range.

PART 2
Two digits are indices in the string.
One and only one must contain the char.
"""
import re
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
1-3 a: abcde
1-3 b: cdefg
2-9 c: ccccccccc
"""
PART_ONE_EXAMPLE_RESULT = 2
PART_ONE_RESULT = 383
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 1
PART_TWO_RESULT = None

LINE_RE = re.compile(r"(?P<low>\d+)-(?P<high>\d+) (?P<ch>[a-z]): (?P<test>[a-z]+)")


def part_one(lines: Iterable[str]) -> int:
    def is_valid(line: str) -> bool:
        if (m := LINE_RE.match(line)) is not None:
            return (
                int(m.group("low"))
                <= m.group("test").count(m.group("ch"))
                <= int(m.group("high"))
            )
        raise ValueError("Didn't match line \"" + line + '"')

    return sum(is_valid(line) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    def is_valid(line: str) -> bool:
        if (m := LINE_RE.match(line)) is not None:
            test = m.group("test")
            ch = m.group("ch")
            return (test[int(m.group("low")) - 1] == ch) ^ (
                test[int(m.group("high")) - 1] == ch
            )
        raise ValueError("Didn't match line \"" + line + '"')

    return sum(is_valid(line) for line in lines)
