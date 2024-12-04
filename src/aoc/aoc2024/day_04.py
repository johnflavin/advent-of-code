#!/usr/bin/env python
"""
PART 1
How many times does "XMAS" appear in the word search?

PART 2
How many times does a "MAS" cross (an X-MAS) appear?
"""
import functools
import itertools
import itertools as itt
import logging
from collections.abc import Iterable

from aoc.util import Coord


PART_ONE_EXAMPLE = """\
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX
"""
PART_ONE_EXAMPLE_RESULT = 18
PART_ONE_RESULT = 2571
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 9
PART_TWO_RESULT = 1992

log = logging.getLogger(__name__)


def add(x: Coord, y: Coord) -> Coord:
    return x[0] + y[0], x[1] + y[1]


def part_one(lines: Iterable[str]) -> int:

    grid = [line for line in lines if line]
    num_rows = len(grid)
    num_cols = len(grid[0])

    def on_grid(pt: Coord) -> bool:
        return 0 <= pt[0] < num_rows and 0 <= pt[1] < num_cols

    @functools.cache
    def check_spot(pt: Coord, letter: str) -> bool:
        """Is this spot on the grid, and is that letter at this spot?"""
        if log.isEnabledFor(logging.DEBUG):
            og = on_grid(pt)
            log.debug("%s on grid %s", pt, og)
            if og:
                log.debug(
                    "grid[%s][%s] = %s == %s = %s",
                    pt[0],
                    pt[1],
                    grid[pt[0]][pt[1]],
                    letter,
                    grid[pt[0]][pt[1]] == letter,
                )
        return on_grid(pt) and grid[pt[0]][pt[1]] == letter

    def generate_pts(start_pt: Coord, delta: Coord, seq_len: int) -> Iterable[Coord]:
        log.debug("Checking %s in direction %s", start_pt, delta)
        return itt.accumulate(itt.repeat(delta, seq_len - 1), add, initial=start_pt)

    def check_points(pts: Iterable[Coord], letters: str) -> bool:
        """Check if a sequence of coords contain a sequence of letters"""
        return all(check_spot(pt, letter) for pt, letter in zip(pts, letters))

    letter_sequence = "XMAS"
    return sum(
        check_points(
            itertools.islice(generate_pts(pt, delta, len(letter_sequence)), 1, None),
            letter_sequence[1:],
        )
        for r in range(num_rows)
        for c in range(num_cols)
        for step in (1, -1)
        for delta in ((0, step), (step, 0), (step, step), (step, -step))
        if check_spot(pt := (r, c), "X")
    )


def part_two(lines: Iterable[str]) -> int:

    grid = [line for line in lines if line]
    num_rows = len(grid)
    num_cols = len(grid[0])

    def on_grid(pt: Coord) -> bool:
        return 0 <= pt[0] < num_rows and 0 <= pt[1] < num_cols

    @functools.cache
    def check_spot(pt: Coord, letter: str) -> bool:
        """Is this spot on the grid, and is that letter at this spot?"""
        if log.isEnabledFor(logging.DEBUG):
            og = on_grid(pt)
            log.debug("%s on grid %s", pt, og)
            if og:
                log.debug(
                    "grid[%s][%s] = %s == %s = %s",
                    pt[0],
                    pt[1],
                    grid[pt[0]][pt[1]],
                    letter,
                    grid[pt[0]][pt[1]] == letter,
                )
        return on_grid(pt) and grid[pt[0]][pt[1]] == letter

    def check_points(pts: Iterable[Coord], letters: str) -> bool:
        """Check if a sequence of coords contain a sequence of letters"""
        return all(check_spot(pt, letter) for pt, letter in zip(pts, letters))

    # Find an A, then check if the corners are MMSS (in any possible combination)
    # The way we check the corners is to check if the up-left-down-right diag is
    # MAS or SAM, and independently check if the down-left-up-right diag is
    # MAS or SAM.
    # If any of those four hit, we have an X-MAS.
    return sum(
        any(
            check_points(
                (
                    add(pt, m1_delta),
                    add(pt, m2_delta),
                    add(pt, (-m1_delta[0], -m1_delta[1])),  # S: down left, up right
                    add(pt, (-m2_delta[0], -m2_delta[1])),  # S: down right, up left
                ),
                "MMSS",
            )
            for m1_delta in [(1, 1), (-1, -1)]  # M: Up right, down left
            for m2_delta in [(1, -1), (-1, 1)]  # M: Up left, down right
        )
        for r in range(num_rows)
        for c in range(num_cols)
        if check_spot(pt := (r, c), "A")
    )
