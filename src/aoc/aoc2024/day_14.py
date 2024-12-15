#!/usr/bin/env python
"""
PART 1
Given x,y positions and velocities on a 2D grid.
(+x to the right, +y down)
Space is a torus.
Move everyone for 100 steps.
Answer: multiply together count of robots in each quadrant (ignoring the middle).

PART 2
Find a step where the bots make a picture of a Christmas tree
"""
import itertools
import logging
import math
from collections import Counter, defaultdict
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
p=0,4 v=3,-3
p=6,3 v=-1,-3
p=10,3 v=-1,2
p=2,0 v=2,-1
p=0,0 v=1,3
p=3,0 v=-2,-2
p=7,6 v=-1,-3
p=3,0 v=-1,-2
p=9,3 v=2,3
p=7,3 v=-1,2
p=2,4 v=2,-3
p=9,5 v=-3,-3
"""
PART_ONE_EXAMPLE_BOUNDS = (11, 7)
PART_ONE_BOUNDS = (101, 103)
PART_ONE_EXAMPLE_RESULT = 12
PART_ONE_RESULT = 223020000
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 7338

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)

type V2 = tuple[int, int]


def make_grid_str(bot_positions: Iterable[V2], bounds: V2) -> list[str]:

    def num_to_char(n: int) -> str:
        if n < 10:
            return str(n)
        if n <= 36:
            # Convert 10-35 to a-z
            # 10 -> a (which is 97) so we must + 87
            return chr(n + 87)
        if n < 62:
            # Convert 36-62 to A-Z
            # 36 -> A (65) means + 29
            return chr(n + 29)
        else:
            # We could keep going with symbols and even unicode
            # But I doubt we will get this far
            raise RuntimeError("Too many bots")

    counts = Counter(bot_positions)
    return [
        "".join(
            num_to_char(count) if (count := counts[(x, y)]) else "."
            for x in range(bounds[0])
        )
        for y in range(bounds[1])
    ]


def parse(line: str) -> tuple[V2, V2]:
    return tuple(
        tuple(map(int, pos_or_vel[2:].split(","))) for pos_or_vel in line.split()
    )


def part_one(lines: Iterable[str]) -> int:
    initial_bots = [parse(line) for line in lines]
    is_not_example = any(
        abs(px) > PART_ONE_EXAMPLE_BOUNDS[0] or abs(py) > PART_ONE_EXAMPLE_BOUNDS[1]
        for (px, py), _ in initial_bots
    )

    bounds = PART_ONE_BOUNDS if is_not_example else PART_ONE_EXAMPLE_BOUNDS

    def torus_pos(p: V2, v: V2, t: int) -> V2:
        """Position after t steps"""
        px, py = p
        vx, vy = v
        return (px + t * vx) % bounds[0], (py + t * vy) % bounds[1]

    final_bots = [torus_pos(p, v, 100) for p, v in initial_bots]
    if is_debug:
        for grid_line in make_grid_str(final_bots, bounds):
            log.debug(grid_line)

    middles = tuple((b - 1) // 2 for b in bounds)
    quads = (
        ((0, middles[0]), (0, middles[1])),
        ((0, middles[0]), (middles[1] + 1, bounds[1])),
        ((middles[0] + 1, bounds[0]), (0, middles[1])),
        ((middles[0] + 1, bounds[0]), (middles[1] + 1, bounds[1])),
    )
    return math.prod(
        sum(1 for px, py in final_bots if xmin <= px < xmax and ymin <= py < ymax)
        for (xmin, xmax), (ymin, ymax) in quads
    )


def part_two(lines: Iterable[str]) -> int:
    initial_bots = [parse(line) for line in lines]
    is_not_example = any(
        abs(px) > PART_ONE_EXAMPLE_BOUNDS[0] or abs(py) > PART_ONE_EXAMPLE_BOUNDS[1]
        for (px, py), _ in initial_bots
    )

    bounds = PART_ONE_BOUNDS if is_not_example else PART_ONE_EXAMPLE_BOUNDS

    def torus_pos(p: V2, v: V2, t: int) -> V2:
        """Position after t steps"""
        px, py = p
        vx, vy = v
        return (px + t * vx) % bounds[0], (py + t * vy) % bounds[1]

    def bots_in_row(bots: list[V2], n: int, is_rowwise: bool) -> bool:
        ones = [1] * n
        collections = defaultdict(set)
        for x, y in bots:
            if is_rowwise:
                collections[y].add(x)
            else:
                collections[x].add(y)
        for idx, collection in collections.items():
            # Scan along the row looking for a run of n occupied cells
            diffs = [b - a for a, b in itertools.pairwise(sorted(collection))]
            if any(diffs[i : i + n] == ones for i in range(len(diffs) - n)):
                return True
        return False

    for t in range(bounds[0] * bounds[1]):
        bots = [torus_pos(p, v, t) for p, v in initial_bots]
        if bots_in_row(bots, 20, True) and bots_in_row(bots, 20, False):
            grid = make_grid_str(bots, bounds)
            for grid_line in grid:
                log.info(grid_line)
            log.info("t=%d", t)
            break

    return t
