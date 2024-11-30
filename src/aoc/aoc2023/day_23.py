#!/usr/bin/env python
"""

PART 1
Given a path. Start in the top left, end on the bottom right.
Any slopes must be traversed in the direction they point.
What is the longest path?

PART 2
Ignore slopes
"""
import logging
from collections import deque
from collections.abc import Iterable
from functools import cache

from aoc.util import Coord, OFFSETS


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
PART_TWO_RESULT = 6670


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)

SLOPES = ("^", "<", "v", ">")
OFFSETS_BY_SLOPE = dict(zip(SLOPES, OFFSETS))


def find_path_edges(
    lines: tuple[str, ...], ignore_slopes: bool = False
) -> tuple[tuple[int, tuple[Coord, ...]], ...]:
    rows = len(lines)
    cols = len(lines[0])
    start = (0, lines[0].find("."))
    end = (rows - 1, lines[-1].find("."))

    @cache
    def find_path_segment(
        pt: Coord, prev_point: Coord | None = None
    ) -> tuple[Coord, int, tuple[Coord, ...]]:
        seen = set()
        if prev_point is not None:
            seen.add(prev_point)
        path_len = 1
        while True:
            if is_debug:
                log.debug(f" + {pt}")
            seen.add(pt)
            current_symbol = lines[pt[0]][pt[1]]
            offsets = (
                OFFSETS
                if ignore_slopes or current_symbol not in SLOPES
                else (OFFSETS_BY_SLOPE[current_symbol],)
            )
            next_steps: list[Coord] = [
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
                path_len += 1
            else:
                if is_debug:
                    if not next_steps:
                        log.debug(" ++ End of path. No next steps.")
                    else:
                        log.debug(f" ++ Choices: {next_steps}")
                return pt, path_len, tuple(next_steps)

    find_path_segment.cache_clear()
    paths = []
    frontier: deque[tuple[int, tuple[Coord, ...], Coord]] = deque(
        [(0, (start,), start)]
    )
    while frontier:
        path_len, path, next_step = frontier.popleft()
        prev_step = path[-1] if path[-1] != next_step else None
        if is_debug:
            log.debug(f"find_path_segment({next_step}, {prev_step})")
        next_step_end_node, next_step_len, next_next_steps = find_path_segment(
            next_step, prev_step
        )
        if next_step_end_node in path:
            continue
        path_len += next_step_len
        path = (*path, next_step_end_node)
        if next_step_end_node == end:
            paths.append((path_len, path))
            continue
        frontier.extend((path_len, path, step) for step in next_next_steps)

    return tuple(paths)


def find_max_path_len(lines: Iterable[str], ignore_slopes=False) -> int:
    lines = tuple(lines)
    paths = find_path_edges(lines, ignore_slopes)
    return max(path_len for path_len, _ in paths) - 1


def part_one(lines: Iterable[str]) -> int:
    return find_max_path_len(lines)


def part_two(lines: Iterable[str]) -> int:
    return find_max_path_len(tuple(lines), ignore_slopes=True)
