#!/usr/bin/env python
"""
PART 1
In a 3D space, given a 2D plane of active pts.
Update rule: active pts stay active if they have 2 or 3 active neighbors,
    inactive points turn active if they have 3 active neighbors.
Count active pts after 6 rounds.

PART 2
Now the space is 4D
"""
import itertools
from collections import defaultdict
from collections.abc import Callable, Iterable

from aoc.util import vadd


PART_ONE_EXAMPLE = """\
.#.
..#
###
"""
PART_ONE_EXAMPLE_RESULT = 112
PART_ONE_RESULT = 240
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 848
PART_TWO_RESULT = 1180


type Pt = tuple[int, int, int, int]

zero = {
    3: (0,) * 3,
    4: (0,) * 4,
}


def parse(lines: Iterable[str]) -> set[Pt]:
    return {
        (x, y, 0, 0)
        for y, line in enumerate(lines)
        for x, c in enumerate(line)
        if c == "#"
    }


def neighbors3(pt: Pt) -> Iterable[Pt]:
    for delta in itertools.product((1, 0, -1), repeat=3):
        if delta == zero[3]:
            continue
        add3 = vadd(pt[:3], delta)
        yield *add3, 0


def neighbors4(pt: Pt) -> Iterable[Pt]:
    for delta in itertools.product((1, 0, -1), repeat=4):
        if delta == zero[4]:
            continue
        yield vadd(pt, delta)


def apply_rules(active: set[Pt], neighbors: Callable[[Pt], Iterable[Pt]]) -> set[Pt]:
    new_active = set()
    inactive_pt_active_neighbors_dict = defaultdict(int)
    for pt in active:
        active_pt_active_neighbors = 0
        # Look at all neighbors of this active pt
        for n in neighbors(pt):
            if n in active:
                # This active pt has an active neighbor
                active_pt_active_neighbors += 1
            else:
                # This inactive n has an active neighbor pt
                inactive_pt_active_neighbors_dict[n] += 1
        if active_pt_active_neighbors == 2 or active_pt_active_neighbors == 3:
            new_active.add(pt)

    new_active.update(
        n
        for n, inactive_pt_active_neighbors in inactive_pt_active_neighbors_dict.items()
        if inactive_pt_active_neighbors == 3
    )

    return new_active


def part_one(lines: Iterable[str]) -> int:
    active = parse(lines)
    for _ in range(6):
        active = apply_rules(active, neighbors3)
    return len(active)


def part_two(lines: Iterable[str]) -> int:
    active = parse(lines)
    for _ in range(6):
        active = apply_rules(active, neighbors4)
    return len(active)
