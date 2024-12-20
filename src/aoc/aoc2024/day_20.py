#!/usr/bin/env python
"""
PART 1
Path finding but you can "cheat" by going through walls for up to two steps.
How many cheat locations (start, end pair) would save >= 100 steps?

PART 2
Cheats can go up to 20 steps
"""
import heapq
from collections.abc import Iterable

from aoc.util import Coord, neighbors, manhattan_distance


PART_ONE_EXAMPLE = """\
###############
#...#...#.....#
#.#.#.#.#.###.#
#S#...#.#.#...#
#######.#.#.###
#######.#.#...#
#######.#.###.#
###..E#...#...#
###.#######.###
#...###...#...#
#.#####.#.###.#
#.#...#.#.#...#
#.#.#.#.#.#.###
#...#...#...###
###############
"""
THRESHOLD = 100
PART_ONE_EXAMPLE_RESULT = 44
PART_ONE_EXAMPLE_THRESHOLD = 2
PART_ONE_RESULT = 1448
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 285
PART_TWO_EXAMPLE_THRESHOLD = 50
PART_TWO_RESULT = 1017615

# For each location, how many steps from here to the end (no cheating)
type Guide = dict[Coord, int]
type Cheat = tuple[Coord, Coord]
type Cheats = dict[Cheat, int]


def walk(
    start: Coord, end: Coord, walls: set[Coord], guide: Guide | None = None
) -> Guide:
    guide = guide or {}

    # Shortcut
    if start in guide:
        return guide

    # (estimated steps to end, actual steps so far, pt)
    steps = 0
    pt = start
    null_pt = (-1, -1)
    frontier = [(0, steps, pt, null_pt)]
    visited = {}

    while frontier:
        _, steps, pt, prev_pt = heapq.heappop(frontier)
        if pt in visited:
            continue
        visited[pt] = prev_pt

        if pt == end or pt in guide:
            break

        for n in neighbors(pt):
            if n in visited or n in walls:
                continue
            next_steps = steps + 1
            heuristic = next_steps + manhattan_distance(n, end)
            heapq.heappush(frontier, (heuristic, next_steps, n, pt))

    if pt == end:
        # We found end without the guide.
        steps_to_end = 0
        guide[end] = 0
    else:
        steps_to_end = guide[pt]

    # Walk back to start and add a step for each pt
    while (pt := visited[pt]) is not null_pt:
        steps_to_end += 1
        guide[pt] = steps_to_end

    return guide


def cheat_walk(
    cheat_step_limit: int, start: Coord, end: Coord, walls: set[Coord]
) -> Cheats:
    # Vanilla
    guide = walk(start, end, walls)
    vanilla = guide[start]
    # (cheat_start, cheat_end): steps saved
    cheats = {}

    # Find boundaries so we don't walk out into space
    max_x, max_y = 0, 0
    for wx, wy in walls:
        if wx > max_x:
            max_x = wx
        if wy > max_y:
            max_y = wy

    def in_bounds(pt: Coord):
        x, y = pt
        return 0 <= x <= max_x and 0 <= y <= max_y

    queue = [(0, start)]
    visited = set()
    while queue:
        steps, pt = heapq.heappop(queue)
        if pt in visited:
            continue
        visited.add(pt)

        # Regular walking, no cheats
        for n in neighbors(pt):
            if n in visited:
                continue
            if n not in walls:
                heapq.heappush(queue, (steps + 1, n))

        # Try cheating from here
        cqueue = [(0, pt)]
        cheat_visited = set()
        while cqueue:
            csteps, cpt = heapq.heappop(cqueue)
            if cpt in cheat_visited:
                continue
            cheat_visited.add(cpt)
            if cpt not in walls and (pt, cpt) not in cheats:
                # This is a cheat exit
                guide = walk(cpt, end, walls, guide)
                steps_to_end = guide[cpt]
                total_steps = steps + csteps + steps_to_end
                cheats[(pt, cpt)] = vanilla - total_steps
            if csteps < cheat_step_limit:
                # Keep cheating, add neighbors
                for n in neighbors(cpt):
                    next_csteps = csteps + 1
                    if in_bounds(n) and n not in cheat_visited:
                        heapq.heappush(cqueue, (next_csteps, n))

    return cheats


def parse(lines: Iterable[str]) -> tuple[Coord, Coord, set[Coord]]:
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


def do_the_thing(lines: Iterable[str], cheat_step_limit: int, part1: bool) -> int:
    start, end, walls = parse(lines)

    is_example = start == (1, 3) and end == (5, 7)
    threshold = (
        THRESHOLD
        if not is_example
        else PART_ONE_EXAMPLE_THRESHOLD if part1 else PART_TWO_EXAMPLE_THRESHOLD
    )

    cheats = cheat_walk(cheat_step_limit, start, end, walls)

    return sum(steps >= threshold for steps in cheats.values())


def part_one(lines: Iterable[str]) -> int:
    return do_the_thing(lines, 2, part1=True)


def part_two(lines: Iterable[str]) -> int:
    return do_the_thing(lines, 20, part1=False)
