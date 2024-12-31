#!/usr/bin/env python
"""
PART 1
Given a square filled with letters.
Find the connected areas where letters are adjacent.
Find the area (size / number of nodes) and perimeter
"Price" is area * perimeter
Sum prices

PART 2
"Price" is now area * number of sides
Sum prices

To find number of sides, we need only count number of vertices.
Make sure we double count vertices like the one in the middle of
AAAAAA
AAABBA
AAABBA
ABBAAA
ABBAAA
AAAAAA
"""
import functools
import itertools
import logging
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field

from aoc.util import Pt, neighbors, add

PART_ONE_EXAMPLE = """\
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
"""
PART_ONE_EXAMPLE_RESULT = 1930
PART_ONE_RESULT = 1486324
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 1206
PART_TWO_RESULT = 898684


log = logging.getLogger(__name__)


def perimeter(pts: set[Pt]) -> int:
    return sum(4 - sum(1 for n in neighbors(pt) if n in pts) for pt in pts)


def neighbors_and_diags(pt: Pt) -> Iterable[tuple[Pt, Pt, Pt]]:
    """Return an iterable of each diagonal along with its two adjacent neighbors"""
    add_p = functools.partial(add, pt)
    for trio in (
        ((1, 0), (1, 1), (0, 1)),
        ((-1, 0), (-1, -1), (0, -1)),
        ((1, 0), (1, -1), (0, -1)),
        ((-1, 0), (-1, 1), (0, 1)),
    ):
        yield tuple(map(add_p, trio))


def find_num_corners(pts: set[Pt]) -> int:
    def is_exterior_corner(neighbor1: Pt, neighbor2: Pt) -> bool:
        """Both neighbors are not in pts"""
        return pts.isdisjoint({neighbor1, neighbor2})

    def is_interior_corner(neighbor1: Pt, diag: Pt, neighbor2: Pt) -> bool:
        """Diag not in pts, neighbors both are in pts"""
        return diag not in pts and {neighbor1, neighbor2} < pts

    return sum(
        (
            is_exterior_corner(neighbor1, neighbor2)
            or is_interior_corner(neighbor1, diag, neighbor2)
        )
        for pt in pts
        for neighbor1, diag, neighbor2 in neighbors_and_diags(pt)
    )


def num_sides(pts: set[Pt]) -> int:
    return find_num_corners(pts)


@dataclass
class Area:
    pts: set[Pt] = field(default_factory=set)

    @property
    def perimeter(self):
        return perimeter(self.pts)

    @property
    def area(self):
        return len(self.pts)

    @property
    def num_sides(self):
        return num_sides(self.pts)

    @property
    def price_part_one(self):
        return self.area * self.perimeter

    @property
    def price_part_two(self):
        return self.area * self.num_sides


def flood_fill(seed: Pt, grid: list[str]) -> Area:
    max_r = len(grid)
    max_c = len(grid[0])

    def inbounds(a: Pt) -> bool:
        return 0 <= a[0] < max_r and 0 <= a[1] < max_c

    area = Area()
    label = grid[seed[0]][seed[1]]
    queue = {seed}
    while queue:
        pt = queue.pop()
        area.pts.add(pt)
        queue.update(
            n
            for n in neighbors(pt)
            if inbounds(n) and grid[n[0]][n[1]] == label and n not in area.pts
        )
    return area


def find_areas(grid: list[str]) -> dict[str, list[Area]]:
    log.debug("Grid %s", grid)
    all_areas = defaultdict(list)
    found_pts = {}
    yet_to_be_found_pts = set(itertools.product(range(len(grid)), range(len(grid[0]))))
    log.debug("Looking for pts %s", yet_to_be_found_pts)
    while yet_to_be_found_pts:
        seed = yet_to_be_found_pts.pop()
        log.debug("Seed %s", seed)

        area = flood_fill(seed, grid)
        log.debug("Area %s", area)

        all_areas[grid[seed[0]][seed[1]]].append(area)
        found_pts.update(area.pts)
        yet_to_be_found_pts.difference_update(area.pts)

    return all_areas


def part_one(lines: Iterable[str]) -> int:
    grid = list(lines)
    all_areas = find_areas(grid)
    return sum(
        sum(area.price_part_one for area in areas) for areas in all_areas.values()
    )


def part_two(lines: Iterable[str]) -> int:
    grid = list(lines)
    all_areas = find_areas(grid)
    return sum(
        sum(area.price_part_two for area in areas) for areas in all_areas.values()
    )
