#!/usr/bin/env python
"""
PART 1
Calculate pseudorandom numbers from a seed
Sum result of running process 2000 times for each seed

PART 2
price = secret number % 10
Across all seeds, find sequences of 2000 secrets, find prices, find diff sequences.
Look for a window of 4 diffs such that the sum of the prices at the end of that window
    across all seeds is maximized.
"""
import itertools
import logging
from collections.abc import Iterable
from typing import Callable

PART_ONE_EXAMPLE = """\
1
10
100
2024
"""
PART_ONE_EXAMPLE_RESULT = 37327623
PART_ONE_RESULT = 17262627539
PART_TWO_EXAMPLE = """\
1
2
3
2024
"""
PART_TWO_EXAMPLE_RESULT = 23
PART_TWO_RESULT = 1986


log = logging.getLogger(__name__)


def repeat[T](f: Callable[[T], T], n: int, initial: T) -> T:
    x = initial
    for _ in range(n):
        x = f(x)
    return x


def iter_repeat[T](f: Callable[[T], T], n: int, initial: T) -> Iterable[T]:
    x = initial
    yield x
    for _ in range(n):
        x = f(x)
        yield x
    return x


def secret_func(n: int) -> int:
    n = ((n << 6) ^ n) % 16777216
    n = ((n >> 5) ^ n) % 16777216
    n = ((n << 11) ^ n) % 16777216
    return n


def part_one(lines: Iterable[str]) -> int:
    return sum(repeat(secret_func, 2000, int(line)) for line in lines)


def find_diff_price_map(initial: int, num: int) -> dict[tuple[int, ...], int]:
    prices = tuple(x % 10 for x in iter_repeat(secret_func, num, initial))
    diffs = tuple(b - a for a, b in itertools.pairwise(prices))
    dpm = {}
    for i, p in enumerate(prices[4:]):
        d = tuple(diffs[i : i + 4])
        if d in dpm:
            continue
        dpm[d] = p
    return dpm


def part_two(lines: Iterable[str]) -> int:
    diff_price_maps = [find_diff_price_map(int(line), 2000) for line in lines]
    all_diffs = set(itertools.chain.from_iterable(d.keys() for d in diff_price_maps))
    if log.isEnabledFor(logging.DEBUG):
        max_s = -1
        for d in all_diffs:
            ps = [dp_map[d] for dp_map in diff_price_maps if d in dp_map]
            s = sum(ps)
            log.debug("%s %s = %d", ",".join(map(str, d)), " + ".join(map(str, ps)), s)
            if s > max_s:
                log.debug("max = %d", s)
                max_s = s
        return max_s
    return max(sum(dp_map.get(d, 0) for dp_map in diff_price_maps) for d in all_diffs)
