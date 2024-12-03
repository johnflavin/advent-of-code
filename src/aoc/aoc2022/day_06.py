#!/usr/bin/env python
"""
PART 1
Given a string of random-ish characters, find the first occurrence of
a window of 4 different characters. Report the length of the string so
far, including the window.

PART 2
Same as part 1 but we need to look for windows of 14 characters.
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw
"""
PART_ONE_EXAMPLE_RESULT = 11
PART_ONE_RESULT = 1640
PART_TWO_EXAMPLE = """\
nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg
"""
PART_TWO_EXAMPLE_RESULT = 29
PART_TWO_RESULT = 3613


def find_different_chars(line: str, window_size: int) -> int:
    for window_start_idx in range(0, len(line)):
        if (
            len(set(line[window_start_idx : window_start_idx + window_size]))
            == window_size
        ):
            return window_start_idx + window_size
    return 0


def part_one(lines: Iterable[str]) -> int:
    return find_different_chars("".join(lines), 4)


def part_two(lines: Iterable[str]) -> int:
    return find_different_chars("".join(lines), 14)
