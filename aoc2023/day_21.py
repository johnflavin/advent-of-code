#!/usr/bin/env python
"""

PART 1
Given a map of a garden with path ".", rocks "#", and starting position "S".
How many locations can be reached from start in 64 steps?

Discussion
Isn't it just half the size of the map - number of rocks?

I've gone through a few iterations of this trying to avoid actual pathfinding.
I think I'm close, but I think I may need to implement actual pathfinding. :(
Looks like there are a few points around the edge where my implementation thinks you
    could reach just from the raw index calculations, but you couldn't actually
    reach within 64 steps.

Spoiler from part 2: pathfinding will not be effective at all.

PART 2

"""

from .util import Coord
from collections import deque
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
...........
"""
PART_ONE_EXAMPLE_RESULT = 42
PART_ONE_RESULT = 3598  # < 3600, > 3344
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None

OFFSETS = (
    (-1, 0),
    (0, -1),
    (1, 0),
    (0, 1),
)


def part_one(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    garden = list(lines)
    num_rows = len(garden)
    num_cols = len(garden[0])

    starts = [
        (row_idx, col_idx)
        for row_idx, line in enumerate(garden)
        for col_idx, ch in enumerate(line)
        if ch == "S"
    ]
    start = starts[0]
    start_mod = (start[0] + start[1]) % 2

    def neighbors(pt: Coord) -> Iterable[Coord]:
        for row_off, col_off in OFFSETS:
            yield pt[0] + row_off, pt[1] + col_off

    seen = set()
    dists = {}
    frontier = deque([(start, 0)])
    while frontier:
        pt, dist = frontier.popleft()

        if pt in seen:
            continue
        seen.add(pt)

        if (
            not (-1 < pt[0] < num_rows and -1 < pt[1] < num_cols)
            or garden[pt[0]][pt[1]] == "#"
        ):
            continue

        dists[pt] = dist

        frontier.extend((neighbor, dist + 1) for neighbor in neighbors(pt))

    # print("Input:")
    # print("\n".join(garden))
    #
    # visitable_garden = [
    #     "".join(
    #         "O"
    #         if (row_idx, col_idx) in dists
    #         and (dist := dists[(row_idx, col_idx)]) % 2 == start_mod
    #         and dist <= 64
    #         else ch
    #         for col_idx, ch in enumerate(line)
    #     )
    #     for row_idx, line in enumerate(garden)
    # ]
    # print("Visitable:")
    # visitable_str = "\n".join(visitable_garden)
    # print(visitable_str)
    # num_visitable = visitable_str.count("O")
    # print("Num visitable: ", num_visitable)

    return sum(1 for dist in dists.values() if dist <= 64 and dist % 2 == start_mod)


def part_two(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    return -1
