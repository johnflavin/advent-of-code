#!/usr/bin/env python
"""
PART 1
Compare nested lists of ints
Ordering rules:
- int v int: left <= right
- list v list: compare items, must reach end of left before right
- list v int: Convert int to list[int], continue comparison

PART 2
Sort all the packets, plus two divider packets [[2]] and [[6]].
Find the indices of the divider packets in the sorted result (1-based)
and multiply them together.

Sorting should be straightforward using the comparison function I
already wrote for part 1. Just pass it to sorted's key param using
functools.cmp_to_key.
(I learned about this technique solving 2024-12-05, which is actually today
at time of writing!)
"""
import functools
import itertools
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
"""
PART_ONE_EXAMPLE_RESULT = 13
PART_ONE_RESULT = 5506
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 140
PART_TWO_RESULT = 21756


log = logging.getLogger(__name__)


type Thing = list[int] | list["Thing"]


def compare(left: Thing, right: Thing) -> int:
    """Return -1 if left < right, 0 if left == right, 1 if left > right"""
    log.debug("compare left %s", left)
    log.debug("compare right %s", right)
    left_l = len(left)
    right_l = len(right)
    idx = 0
    while idx < right_l or idx < left_l:
        if left_l <= idx < right_l:
            # Ran out of left elements before right
            log.debug("len(left) %d <= idx %d < len(right) %d", left_l, idx, right_l)
            return -1
        if right_l <= idx < left_l:
            # Ran out of right elements before left
            log.debug("len(right) %d <= idx %d < len(left) %d", right_l, idx, left_l)
            return 1
        left_item = left[idx]
        right_item = right[idx]

        if isinstance(left_item, int) and isinstance(right_item, int):
            if left_item > right_item:
                log.debug("left %d > right %d", left_item, right_item)
                return 1
            elif left_item < right_item:
                log.debug("left %d < right %d", left_item, right_item)
                return -1
            # If they're equal, keep looking
            log.debug("left %d == right %d", left_item, right_item)
        else:
            # Either both are lists, or one is a list and one an int
            # In the latter case we coerce into two lists
            if isinstance(left_item, list) and isinstance(right_item, int):
                log.debug("right %d -> [%d]", right_item, right_item)
                right_item = [right_item]
            elif isinstance(left_item, int) and isinstance(right_item, list):
                log.debug("left %d -> [%d]", left_item, left_item)
                left_item = [left_item]
            # Recurse
            comparison = compare(left_item, right_item)
            if comparison != 0:
                return comparison
            # If they're equal, keep looking

        # Next iteration
        idx += 1
    log.debug("left %s == right %s", left, right)
    return 0


def parse_input(lines: Iterable[str]) -> Iterable[tuple[Thing, Thing]]:
    for line_batch in itertools.batched(lines, 3):
        yield eval(line_batch[0]), eval(line_batch[1])


def part_one(lines: Iterable[str]) -> int:
    inputs = parse_input(lines)

    s = 0
    for idx, (left, right) in enumerate(inputs, 1):
        log.debug("input %d", idx)
        if compare(left, right) == -1:
            log.debug("sum %d + idx %d = %d", s, idx, s + idx)
            s += idx
        else:
            log.debug("input %d is not in order", idx)
    return s


def part_two(lines: Iterable[str]) -> int:
    divider1 = [[2]]
    divider2 = [[6]]
    inputs = parse_input(lines)
    all_packets = [divider1, divider2] + list(itertools.chain.from_iterable(inputs))
    sorted_packets = sorted(all_packets, key=functools.cmp_to_key(compare))
    divider1_idx = sorted_packets.index(divider1)
    divider2_idx = sorted_packets.index(divider2)
    return (divider1_idx + 1) * (divider2_idx + 1)
