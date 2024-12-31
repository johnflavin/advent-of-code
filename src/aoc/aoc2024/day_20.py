#!/usr/bin/env python
"""
PART 1
Path finding but you can "cheat" by going through walls for up to two steps.
How many cheat locations (start, end pair) would save >= 100 steps?

PART 2
Cheats can go up to 20 steps
"""
from collections.abc import Iterable

from aoc.util import Pt, neighbors


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


def find_dist_from_start(start: Pt, end: Pt, walls: set[Pt]) -> dict[Pt, int]:
    dist_from_start = {start: 0}
    pt = start
    while pt != end:
        for next_pt in neighbors(pt):
            if next_pt not in dist_from_start and next_pt not in walls:
                dist_from_start[next_pt] = dist_from_start[pt] + 1
                pt = next_pt

    return dist_from_start


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


def count_cheat_savings(
    lines: Iterable[str], cheat_step_limit: int, part1: bool
) -> int:
    start, end, walls = parse(lines)

    is_example = start == (1, 3) and end == (5, 7)
    threshold = (
        THRESHOLD
        if not is_example
        else PART_ONE_EXAMPLE_THRESHOLD if part1 else PART_TWO_EXAMPLE_THRESHOLD
    )

    dist_from_start = find_dist_from_start(start, end, walls)

    cheat_savings = 0
    for cstart, d_cstart_start in dist_from_start.items():
        csx, csy = cstart
        for dx in range(-cheat_step_limit, cheat_step_limit + 1):
            adx = abs(dx)
            remaining_y = cheat_step_limit - adx
            for dy in range(-remaining_y, remaining_y + 1):
                cend = (csx + dx, csy + dy)
                if (d_cend_start := dist_from_start.get(cend, -1)) == -1:
                    # This covers walls and OOB
                    continue
                savings = d_cend_start - d_cstart_start - adx - abs(dy)
                if savings >= threshold:
                    cheat_savings += 1
    return cheat_savings


def part_one(lines: Iterable[str]) -> int:
    return count_cheat_savings(lines, 2, part1=True)


def part_two(lines: Iterable[str]) -> int:
    return count_cheat_savings(lines, 20, part1=False)
