#!/usr/bin/env python
"""
PART 1
Given a sequence of starting numbers, continue the sequence according to a rule.
If the last number was new, emit 0.
Otherwise, emit the difference between the last turn index and the previous
    turn when the number was last spoken.
What is the 2020th number?

PART 2
What is the 30000000th number?

(I'm shocked that brute force seems to work just fine here.
It takes a while but I'm ok with that.)
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
0,3,6
"""
PART_ONE_EXAMPLE_RESULT = 436
PART_ONE_RESULT = 1085
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 175594
PART_TWO_RESULT = 10652


def run(lines: Iterable[str], limit: int) -> int:
    nums = tuple(map(int, "".join(lines).split(",")))

    n = -1
    next_spoken = -1
    last_spoken_turns = {}
    for i, n in enumerate(nums):
        turn = i + 1
        next_spoken = 0 if n not in last_spoken_turns else turn - last_spoken_turns[n]
        last_spoken_turns[n] = turn

    for i in range(len(nums), limit):
        turn = i + 1
        n = next_spoken
        next_spoken = 0 if n not in last_spoken_turns else turn - last_spoken_turns[n]
        last_spoken_turns[n] = turn

    return n


def part_one(lines: Iterable[str]) -> int:
    return run(lines, 2020)


def part_two(lines: Iterable[str]) -> int:
    return run(lines, 30000000)
