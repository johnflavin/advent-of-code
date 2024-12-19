#!/usr/bin/env python
"""
PART 1
Given voxel positions, count surface area not touching another voxel

PART 2
Only count exterior surface area
"""

import logging
from collections.abc import Iterable

from aoc.util import vadd


PART_ONE_EXAMPLE = """\
2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5
"""
PART_ONE_EXAMPLE_RESULT = 64
PART_ONE_RESULT = 4418
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 58
PART_TWO_RESULT = 2486

log = logging.getLogger(__name__)


type Voxel = tuple[int, ...]


ADJACENT = (
    (1, 0, 0),
    (-1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
    (0, 0, 1),
    (0, 0, -1),
)


def find_interior_voxels(voxels: set[Voxel]) -> set[Voxel]:
    # Find the bounding box of the voxels to limit our search space
    bbox = [[0, 0], [0, 0], [0, 0]]
    for v in voxels:
        for i in range(3):
            if v[i] < bbox[i][0]:
                bbox[i][0] = v[i]
            elif v[i] > bbox[i][1]:
                bbox[i][1] = v[i]

    def in_bbox(v: Voxel):
        return all(bbox[i][0] <= v[i] <= bbox[i][1] for i in range(3))

    # Flood fill the outside to find what is and isn't interior
    # Start just outside the bounding box so we are guaranteed it is outside, then
    #  keep adding all neighbors we can reach
    queue = set()
    queue.update(
        (x, y, z)
        for x in (bbox[0][0] - 1, bbox[0][1] + 1)
        for y in range(*bbox[1])
        for z in range(*bbox[2])
    )
    queue.update(
        (x, y, z)
        for x in range(*bbox[0])
        for y in (bbox[1][0] - 1, bbox[1][1] + 1)
        for z in range(*bbox[2])
    )
    queue.update(
        (x, y, z)
        for x in range(*bbox[0])
        for y in range(*bbox[1])
        for z in (bbox[2][0] - 1, bbox[2][1] + 1)
    )

    outside = set()
    while queue:
        o = queue.pop()
        outside.add(o)
        queue.update(
            o_neighbor
            for d in ADJACENT
            if (o_neighbor := vadd(o, d)) not in voxels
            and o_neighbor not in outside
            and o_neighbor not in queue
            and in_bbox(o_neighbor)
        )

    # Everything that isn't outside and isn't voxels is interior
    return {
        v
        for x in range(*bbox[0])
        for y in range(*bbox[1])
        for z in range(*bbox[2])
        if (v := (x, y, z)) not in voxels and v not in outside
    }


def count_surface_area(lines: Iterable[str], part1: bool) -> int:
    voxel_positions = set(sorted(tuple(map(int, line.split(","))) for line in lines))

    interior_voxels = set() if part1 else find_interior_voxels(voxel_positions)
    if not part1:
        log.debug("Interior voxels: %s", interior_voxels)

    # Assume all sides are exposed unless a neighbor is in the list
    return sum(
        6
        - sum(
            (neighbor := vadd(v, delta)) in voxel_positions
            or neighbor in interior_voxels
            for delta in ADJACENT
        )
        for v in voxel_positions
    )


def part_one(lines: Iterable[str]) -> int:
    return count_surface_area(lines, part1=True)


def part_two(lines: Iterable[str]) -> int:
    return count_surface_area(lines, part1=False)
