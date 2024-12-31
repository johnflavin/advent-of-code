#!/usr/bin/env python
"""
PART 1
A "trail" is a path from 0–9 that increases by one at each step.
A "trailhead" is the zero of a trail, scored by how many 9s it can
reach.
Sum the scores of all the trailheads.
(= the number of trails)

Scratch that parenthetical. That's wrong.

PART 2
My parenthetical from above is part 2.
Count all distinct trails.
"""
import itertools
import logging
from collections.abc import Iterable
from functools import cache

from aoc.util import Pt, neighbors


PART_ONE_EXAMPLE = """\
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
"""
PART_ONE_EXAMPLE_RESULT = 36
PART_ONE_RESULT = 501
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 81
PART_TWO_RESULT = 1017


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


def part_one(lines: Iterable[str]) -> int:
    """Walk path from all starting points. Return score (number of 9s reachable)."""
    grid = [list(map(int, line)) for line in lines]
    rows = len(grid)
    cols = len(grid[0])

    def inbounds(r: int, c: int) -> bool:
        return 0 <= r < rows and 0 <= c < cols

    @cache
    def find_nines(r: int, c: int) -> set[Pt]:
        """How many 9s can we reach from here?"""
        val = grid[r][c]

        # Base case: return self
        if val == 9:
            log.debug("score (%d, %d) val=%d nines={(%d, %d)}", r, c, val, r, c)
            return {(r, c)}

        s = set(
            itertools.chain.from_iterable(
                find_nines(neighbor_r, neighbor_c)
                for neighbor_r, neighbor_c in neighbors((r, c))
                if inbounds(neighbor_r, neighbor_c)
                and grid[neighbor_r][neighbor_c] == val + 1
            )
        )
        log.debug("score (%d, %d) val=%d nines=%s", r, c, val, s)
        return s

    return sum(
        len(find_nines(r, c))
        for r, row in enumerate(grid)
        for c, val in enumerate(row)
        if val == 0
    )


def part_two(lines: Iterable[str]) -> int:
    """Walk path from all starting points. Return score (number of trails)."""
    grid = [list(map(int, line)) for line in lines]
    rows = len(grid)
    cols = len(grid[0])

    def inbounds(r: int, c: int) -> bool:
        return 0 <= r < rows and 0 <= c < cols

    @cache
    def score(r: int, c: int) -> int:
        """How many trails can we reach from here?"""
        val = grid[r][c]

        # Base case: 1 trail
        if val == 9:
            log.debug("(%d, %d) val=%d score=1", r, c, val)
            return 1

        s = sum(
            score(neighbor_r, neighbor_c)
            for neighbor_r, neighbor_c in neighbors((r, c))
            if inbounds(neighbor_r, neighbor_c)
            and grid[neighbor_r][neighbor_c] == val + 1
        )
        log.debug("(%d, %d) val=%d score=%d", r, c, val, s)
        return s

    return sum(
        score(r, c)
        for r, row in enumerate(grid)
        for c, val in enumerate(row)
        if val == 0
    )
