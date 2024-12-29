#!/usr/bin/env python
"""
PART 1
Find the next bus that will leave after a given time.
Bus ID = multiples of times it will leave
Return time we must wait * bus ID

PART 2
Find a time s.t. the first bus leaves at t, second at t + 1, etc.
"""
import logging
import math
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
939
7,13,x,x,59,x,31,19
"""
PART_ONE_EXAMPLE_RESULT = 295
PART_ONE_RESULT = 203
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 1068781
PART_TWO_RESULT = 905694340256752

log = logging.getLogger(__name__)


def extended_euclid(a: int, b: int) -> tuple[int, int]:
    """See https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm#Pseudocode"""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    return old_s, old_t


def part_one(lines: Iterable[str]) -> int:
    goal_time_str, bus_ids = tuple(lines)
    goal_time = int(goal_time_str)
    return math.prod(
        min(
            (-goal_time % int(bus_id), int(bus_id))
            for bus_id in bus_ids.split(",")
            if bus_id != "x"
        )
    )


def part_two(lines: Iterable[str]) -> int:
    _, bus_ids = tuple(lines)
    crt_info = sorted(
        [(-i, int(bid)) for i, bid in enumerate(bus_ids.split(",")) if bid != "x"]
    )

    # Using Chinese Remainder Theorem, roughly following
    #  https://en.wikipedia.org/wiki/Chinese_remainder_theorem#Using_the_existence_construction
    a, n = crt_info[0]
    log.debug("a=%d n=%d", a, n)
    log.debug("-" * 5)
    for a1, n1 in crt_info[1:]:
        log.debug("a1=%d n1=%d", a1, n1)
        m, m1 = extended_euclid(n, n1)
        log.debug("m=%d m1=%d", m, m1)
        a = a * m1 * n1 + a1 * m * n
        n *= n1
        log.debug("a=%d n=%d", a, n)

        a = a % n
        log.debug("a=%d n=%d", a, n)
        log.debug("-" * 5)
    return a
