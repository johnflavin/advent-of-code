#!/usr/bin/env python
"""

PART 1
Given a path. Start in the top left, end on the bottom right.
Any slopes must be traversed in the direction they point.
What is the longest path?

PART 2
Ignore slopes
"""
import itertools
import logging
from .util import Coord, OFFSETS
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
#.#####################
#.......#########...###
#######.#########.#.###
###.....#.>.>.###.#.###
###v#####.#v#.###.#.###
###.>...#.#.#.....#...#
###v###.#.#.#########.#
###...#.#.#.......#...#
#####.#.#.#######.#.###
#.....#.#.#.......#...#
#.#####.#.#.#########v#
#.#...#...#...###...>.#
#.#.#v#######v###.###v#
#...#.>.#...>.>.#.###.#
#####v#.#.###v#.#.###.#
#.....#...#...#.#.#...#
#.#########.###.#.#.###
#...###...#...#...#.###
###.###.#.###v#####v###
#...#...#.#.>.>.#.>.###
#.###.###.#.###.#.#v###
#.....###...###...#...#
#####################.#
"""
PART_ONE_EXAMPLE_RESULT = 94
PART_ONE_RESULT = 2182
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 154
PART_TWO_RESULT = None


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)

SLOPES = ("^", "<", "v", ">")
OFFSETS_BY_SLOPE = dict(zip(SLOPES, OFFSETS))


def find_longest_path(
    lines: tuple[str, ...], ignore_slopes: bool = False
) -> tuple[Coord, ...]:
    rows = len(lines)
    cols = len(lines[0])
    start = (0, lines[0].find("."))
    end = (rows - 1, lines[-1].find("."))

    def longest_path_from(pt: Coord, seen: set[Coord] = None) -> tuple[Coord, ...]:
        seen = set(seen) if seen is not None else set()
        path = []
        while True:
            if is_debug:
                log.debug(f" + {pt}")
            path.append(pt)
            if pt == end:
                log.debug(" ~~ Found the end ~~")
                return tuple(path)
            seen.add(pt)
            current_symbol = lines[pt[0]][pt[1]]
            offsets = (
                OFFSETS
                if ignore_slopes or current_symbol not in SLOPES
                else (OFFSETS_BY_SLOPE[current_symbol],)
            )
            next_steps = [
                (row, col)
                for offset in offsets
                if (
                    -1 < (row := pt[0] + offset[0]) < rows
                    and -1 < (col := pt[1] + offset[1]) < cols
                    and lines[row][col] != "#"
                    and (row, col) not in seen
                )
            ]
            if len(next_steps) == 1:
                # Just continue stepping forward
                pt = next_steps[0]
            elif len(next_steps) == 0:
                # Seems this path was invalid
                log.debug(" ++ End of path. No next steps.")
                return tuple()
            else:
                # Have to make a choice
                if is_debug:
                    log.debug(f" ++ Recursing into next steps: {next_steps}")
                longest_path_from_here = max(
                    (longest_path_from(neigh, seen) for neigh in next_steps),
                    key=lambda _path: len(_path),
                )
                if is_debug:
                    log.debug(f" + Found longest path from {pt}")
                return *path, *longest_path_from_here

    return longest_path_from(start)


def find_longest_path_len(lines: tuple[str, ...], ignore_slopes: bool = False) -> int:
    lines = tuple(lines)
    longest_path = find_longest_path(lines, ignore_slopes)
    if is_debug:
        path_pts = {}
        for row, row_pts in itertools.groupby(longest_path, lambda pt: pt[0]):
            if row not in path_pts:
                path_pts[row] = set()
            path_pts[row].update(set(pt[1] for pt in row_pts))

        for row, line in enumerate(lines):
            row_pts = path_pts.get(row, set())
            log.debug(
                "".join("O" if col in row_pts else ch for col, ch in enumerate(line))
            )
    return len(longest_path) - 1


def part_one(lines: Iterable[str]) -> int:
    return find_longest_path_len(tuple(lines))


def part_two(lines: Iterable[str]) -> int:
    return find_longest_path_len(tuple(lines), ignore_slopes=True)
