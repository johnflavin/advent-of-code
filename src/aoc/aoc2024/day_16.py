#!/usr/bin/env python
"""
PART 1
It's A* but rotations have a cost

...actually this is really slow.
I think I forgot how to implement A*.
...Ok, got it now. It's fast.

PART 2
Sum number of unique points in *all* best paths.
"""
import heapq
import logging
from collections.abc import Iterable

from aoc.util import Pt, add, sub


PART_ONE_EXAMPLE = """\
###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############
"""
PART_ONE_EXAMPLE_RESULT = 7036
PART_ONE_RESULT = 90460
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 45
PART_TWO_RESULT = 575


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


# E = (1, 0)
# N = (0, -1)
# W = (-1, 0)
# S = (0, 1)


def rotate_cw(pt: Pt) -> Pt:
    return -pt[1], pt[0]


def rotate_ccw(pt: Pt) -> Pt:
    return pt[1], -pt[0]


def walk(start: Pt, end: Pt, walls: set[Pt], part1: bool = True) -> int:

    def heuristic(pt: Pt, facing: Pt) -> int:
        diff = sub(end, pt)
        steps = abs(diff[0]) + abs(diff[1])
        match diff, facing:
            case ((0, d), (0, f)) | ((d, 0), (f, 0)) if d * f > 0:
                rots = 0
            case (dx, dy), (fx, fy) if dx * fx > 0 or dy * fy > 0:
                rots = 1
            case _:
                rots = 2
        return steps + 1000 * rots

    log.debug("start=%s end=%s part1=%s", start, end, part1)

    frontier = []
    visited = {}
    heapq.heappush(frontier, (heuristic(start, (1, 0)), 0, start, (1, 0), (None, None)))
    while frontier:
        _, cost, pt, facing, prev = heapq.heappop(frontier)
        log.debug("cost=%d, pt=%s, facing=%s, prev=%s", cost, pt, facing, prev)

        key = pt, facing
        if key in visited:
            prev_cost, prev_pts = visited[key]
            if prev_cost < cost:
                # We've been here before and it was cheaper
                continue
            elif prev_cost == cost:
                # We've been here before and it cost the same
                visited[key] = (cost, {*prev_pts, prev})
                continue
            else:
                # We've been here before but this is cheaper
                visited[key] = (cost, {prev})
        else:
            # We've not been here before
            visited[key] = (cost, {prev})
        if is_debug:
            cost, prev_pts = visited[key]
            if len(prev_pts) > 1:
                log.debug("pt=%s prev_pts=%s", pt, prev_pts)
        # log.debug("visited=%s", visited)

        if pt == end:
            log.debug("Found end. cost=%d", cost)
            if part1:
                return cost
            else:
                # Unspool the paths
                history = set()
                queue = {key}
                while queue:
                    p, f = queue.pop()
                    if p in history:
                        continue
                    history.add(p)
                    _, prev_pts = visited[(p, f)]
                    if prev_pts == {(None, None)}:
                        # This means we're back at start
                        continue
                    queue.update(prev_pts)

                return len(history)

        for next_pt, next_facing, next_prev, next_cost in (
            (add(pt, facing), facing, (pt, facing), 1),
            (pt, rotate_cw(facing), prev, 1000),
            (pt, rotate_ccw(facing), prev, 1000),
        ):
            if next_pt in walls:
                continue
            actual_cost = cost + next_cost
            est = heuristic(next_pt, next_facing)
            heapq.heappush(
                frontier,
                (actual_cost + est, actual_cost, next_pt, next_facing, next_prev),
            )


def part_one(lines: Iterable[str]) -> int:
    def parse(lines: Iterable[str]) -> tuple[Pt, Pt, set[Pt]]:
        start = (-1, -1)
        end = (-1, -1)
        walls = set()
        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                if ch == "#":
                    walls.add((x, y))
                elif ch == "S":
                    start = (x, y)
                elif ch == "E":
                    end = (x, y)

        return start, end, walls

    start, end, walls = parse(lines)
    return walk(start, end, walls, True)


def part_two(lines: Iterable[str]) -> int:
    def parse(lines: Iterable[str]) -> tuple[Pt, Pt, set[Pt]]:
        start = (-1, -1)
        end = (-1, -1)
        walls = set()
        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                if ch == "#":
                    walls.add((x, y))
                elif ch == "S":
                    start = (x, y)
                elif ch == "E":
                    end = (x, y)

        return start, end, walls

    start, end, walls = parse(lines)
    return walk(start, end, walls, False)
