#!/usr/bin/env python
"""
PART 1
You have a bunch of numbers. You consider a window at the beginning.
If the next number equals the sum of any pair in the window (not themselves equal)
then it is valid.
What is the first invalid number?

PART 2
Find a window which sums to the number in part 1.
Return the sum of the max and min of the window.
"""
import logging
from collections import deque
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
35
20
15
25
47
40
62
55
65
95
102
117
150
182
127
219
299
277
309
576
"""
PART_ONE_EXAMPLE_RESULT = 127
PART_ONE_RESULT = 1930745883
PART_ONE_EXAMPLE_WINDOW = 5
PART_ONE_WINDOW = 25
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 62
PART_TWO_RESULT = 268878261


log = logging.getLogger(__name__)


def part_one(lines: Iterable[str]) -> int:
    nums = list(map(int, lines))
    is_example = len(nums) < PART_ONE_WINDOW
    windowlen = PART_ONE_EXAMPLE_WINDOW if is_example else PART_ONE_WINDOW
    testset = set(nums[:windowlen])
    for i, num in enumerate(nums[windowlen:]):
        if not any(
            (num - testnum) in testset and testnum != 2 * num for testnum in testset
        ):
            return num
        testset.remove(nums[i])
        testset.add(num)

    return -1


def part_two(lines: Iterable[str]) -> int:
    nums = list(map(int, lines))
    is_example = len(nums) < PART_ONE_WINDOW
    target = PART_ONE_EXAMPLE_RESULT if is_example else PART_ONE_RESULT
    log.debug("target %d", target)

    window = deque([])
    for num in nums:
        window.append(num)
        log.debug(window)
        s = sum(window)
        log.debug("sum %d", s)
        if s > target:
            log.debug("Reducing window")
            while (s := sum(window)) > target:
                window.popleft()
        if s == target:
            log.debug("found sum %d", target)
            return min(window) + max(window)

    return -1
