#!/usr/bin/env python
"""
PART 1
Sort numbers, add 0 and x+3 to the ends, count the diffs.
Multiply 1-counts * 3-counts.

PART 2
How many different configurations of adapters are there?
As in, how man ways can we drop one out?
"""
import itertools
import logging
from collections import Counter
from collections.abc import Iterable
from functools import cache

PART_ONE_EXAMPLE = """\
28
33
18
42
31
14
46
20
48
47
24
23
49
45
19
38
39
11
1
32
25
35
8
17
7
9
4
2
34
10
3
"""
PART_ONE_EXAMPLE_RESULT = 220
PART_ONE_RESULT = 1856
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 19208
PART_TWO_RESULT = 2314037239808

log = logging.getLogger(__name__)


def part_one(lines: Iterable[str]) -> int:
    adapters = sorted(map(int, lines))
    adapters = [0] + adapters + [adapters[-1] + 3]
    log.debug("adapters %s", adapters)
    diffs = list(map(lambda pair: pair[1] - pair[0], itertools.pairwise(adapters)))
    log.debug("diffs")
    counts = Counter(diffs)
    return counts[1] * counts[3]


def part_two(lines: Iterable[str]) -> int:
    @cache
    def count_arrangements(diffs: tuple[int]) -> int:
        if not diffs or diffs[0] > 3:
            return 0
        if len(diffs) == 1:
            return 1
        # Two branches: keep it or remove it
        keep = count_arrangements(diffs[1:])
        remove = (
            0
            if (new_d1 := diffs[0] + diffs[1]) > 3
            else count_arrangements((new_d1, *diffs[2:]))
        )
        return keep + remove

    adapters = sorted(map(int, lines))
    adapters = [0] + adapters + [adapters[-1] + 3]
    return count_arrangements(
        tuple(map(lambda pair: pair[1] - pair[0], itertools.pairwise(adapters)))
    )
