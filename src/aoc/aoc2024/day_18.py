#!/usr/bin/env python
"""
PART 1

PART 2
"""
import heapq
import logging
from collections.abc import Iterable

from aoc.util import Coord, neighbors, manhattan_distance


PART_ONE_EXAMPLE = """\
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0
"""
PART_ONE_EXAMPLE_RESULT = 22
PART_ONE_RESULT = 298
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = (6, 1)
PART_TWO_RESULT = (52, 32)
EXAMPLE_BOUNDS = 7
BOUNDS = 71

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


def draw_grid(walls: set[Coord], bounds: int) -> None:
    if not is_debug:
        return
    for y in range(bounds):
        log.debug("".join("#" if (x, y) in walls else "." for x in range(bounds)))


def walk(start: Coord, end: Coord, walls: set[Coord]) -> int:
    # (estimated steps to end, actual steps so far, pt)
    frontier = [(0, 0, start)]
    visited = set()

    while frontier:
        _, steps, pt = heapq.heappop(frontier)
        if pt in visited:
            continue

        if pt == end:
            log.debug("Found end: %d steps", steps)
            return steps
        log.debug("Visited %s", pt)
        visited.add(pt)

        for n in neighbors(pt):
            if n in visited or n in walls:
                continue
            next_steps = steps + 1
            heuristic = next_steps + manhattan_distance(n, end)
            heapq.heappush(frontier, (heuristic, next_steps, n))
    return -1


def part_one(lines: Iterable[str]) -> int:
    positions: list[Coord] = [tuple(map(int, line.split(","))) for line in lines]
    is_example = len(positions) <= 25
    bounds = EXAMPLE_BOUNDS if is_example else BOUNDS
    num_walls = 12 if is_example else 1024

    # Let the first 1024 fall
    walls = set(positions[:num_walls])

    # Add wall around the edges so we aren't constantly checking in bounds
    walls.update((x, y) for x in range(-1, bounds + 1) for y in (-1, bounds))
    walls.update((x, y) for x in (-1, bounds) for y in range(-1, bounds + 1))

    return walk((0, 0), (bounds - 1, bounds - 1), walls)


def part_two(lines: Iterable[str]) -> Coord:
    positions: list[Coord] = [tuple(map(int, line.split(","))) for line in lines]
    is_example = len(positions) <= 25
    bounds = EXAMPLE_BOUNDS if is_example else BOUNDS

    # Binary search through positions
    # We know from part 1 that at least 1024 (or 12 for the example) walls can fall
    # To find the minimum, let's binary search through all the positions.
    has_path_idx = 12 if is_example else 1024
    no_path_idx = len(positions) - 1
    walls = set(positions[:has_path_idx])

    # Add wall around the edges so we aren't constantly checking in bounds
    walls.update((x, y) for x in range(0, bounds) for y in (-1, bounds))
    walls.update((x, y) for x in (-1, bounds) for y in range(0, bounds))

    while has_path_idx + 1 < no_path_idx:
        midpoint_idx = has_path_idx + (no_path_idx - has_path_idx) // 2
        log.debug("Testing idx=%d byte=%s", midpoint_idx, positions[midpoint_idx])
        test_walls = {*walls, *positions[has_path_idx : midpoint_idx + 1]}
        if walk((0, 0), (bounds - 1, bounds - 1), test_walls) == -1:
            log.debug("No path")
            no_path_idx = midpoint_idx
        else:
            log.debug("Valid path")
            has_path_idx = midpoint_idx
            walls = test_walls

    return positions[no_path_idx]
