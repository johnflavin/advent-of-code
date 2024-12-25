#!/usr/bin/env python
"""
PART 1
Keys and locks.
How many (key, lock) pairs are not ruled out by shape?

PART 2
No part two. Merry Christmas!
"""
import itertools
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
#####
.####
.####
.####
.#.#.
.#...
.....

#####
##.##
.#.##
...##
...#.
...#.
.....

.....
#....
#....
#...#
#.#.#
#.###
#####

.....
.....
#.#..
###..
###.#
###.#
#####

.....
.....
.....
#....
#.#..
#.#.#
#####
"""
PART_ONE_EXAMPLE_RESULT = 3
PART_ONE_RESULT = 3327
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 0

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


type KL = tuple[int, int, int, int, int]

keyline = "#####"


def parse(lines: Iterable[str]) -> tuple[list[KL], list[KL]]:
    def get_heights(lb: Iterable[str], looking_for: str) -> KL:
        heights = [0] * 5
        for ln in lb[1:]:
            for i, ch in enumerate(ln):
                if ch == looking_for:
                    heights[i] += 1
        return tuple(heights)

    keys = []
    locks = []
    line_buffer = []
    for line in lines:
        if line == "":
            # process line buffer
            if line_buffer[0] == keyline:
                # Process key
                keys.append(get_heights(line_buffer, "#"))
            else:
                # process lock
                locks.append(get_heights(line_buffer, "."))

            # Reset line buffer
            line_buffer = []
        else:
            line_buffer.append(line)
    # Process final line buffer
    if line_buffer[0] == keyline:
        # Process key
        keys.append(get_heights(line_buffer, "#"))
    else:
        # process lock
        locks.append(get_heights(line_buffer, "."))

    return keys, locks


def is_possible(key: KL, lock: KL) -> bool:
    log.debug("is possible key %s lock %s", key, lock)
    if is_debug:
        for k, l in zip(key, lock):
            kgel = k <= l
            log.debug("k %d <= l %d  %s", k, l, kgel)
            if not kgel:
                return False
        return True
    else:
        return all(k <= l for k, l in zip(key, lock))


def part_one(lines: Iterable[str]) -> int:
    keys, locks = parse(lines)

    return sum(is_possible(key, lock) for key, lock in itertools.product(keys, locks))


def part_two(lines: Iterable[str]) -> int:
    return 0
