#!/usr/bin/env python
"""

PART 1
Given lines of hailstones initial x,y,z and velocity vx,vy,vz at time t=0.
Also, out of band, given limits on the x,y area to search (ignore z).

Examine pairs of hailstones.
Find how many pairs' paths will intersect in the future within the test area.
(And I think that if a given hailstone X intersects A at time ta and B at time tb,
we only count X once for the earliest intersection.)

PART 2
"""

from .util import Coord
from collections.abc import Iterable
from itertools import combinations


PART_ONE_EXAMPLE = """\
19, 13, 30 @ -2,  1, -2
18, 19, 22 @ -1, -1, -2
20, 25, 34 @ -2, -2, -4
12, 31, 28 @ -1, -2, -1
20, 19, 15 @  1, -5, -3
"""
PART_ONE_EXAMPLE_TEST_AREA = [7, 27]
PART_ONE_EXAMPLE_RESULT = 2
PART_ONE_TEST_AREA = [200000000000000, 400000000000000]
PART_ONE_RESULT = 21785
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None


type Vector = tuple[int, int, int]


def find_intersection(
    xy0: Coord, vxvy0: Coord, xy1: Coord, vxvy1: Coord
) -> tuple[float, float, float, float] | tuple[None, None, None, None]:
    """
    X = Vt + X0 => t = (X-X0)/V
    y = vy/vx(x-x0) + y0 = v(x-x0) + y0 (using v=vy/vx)
    If we have two of these, they intersect at
    v0(x-x0) + y0 = v1(x-x1) + y1
    => (v0-v1)x = v0*x0-v1*x1 + y1-y0
    => x = (v0*x0-v1*x1 + y1-y0)/(v0-v1)
    and plugging in for y (using v0, though we should be able to use either)
    y = v0(x-x0) + y0 = v0*x - v0*x0 + y0
      = v0[(v0*x0-v1*x1 + y1-y0)/(v0-v1) - x0] + y0
      = (v0*v1*(x0-x1) + v0*y1 - v1*y0)/(v0-v1)

    We won't have any intersection if v0 == v1
    """
    x0, y0 = xy0
    x1, y1 = xy1
    vx0, vy0 = vxvy0
    vx1, vy1 = vxvy1
    v0 = vy0 / vx0
    v1 = vy1 / vx1
    if v0 == v1:
        # No intersection
        return None, None, None, None
    x = (v0 * x0 - v1 * x1 + y1 - y0) / (v0 - v1)
    y = (v0 * y1 - v1 * y0 + (x0 - x1) * v0 * v1) / (v0 - v1)
    t0 = (x - x0) / vx0
    t1 = (x - x1) / vx1
    return x, y, t0, t1


def parse(line: str) -> tuple[Vector, Vector]:
    pos, vel = line.split(" @ ")
    pos: Vector = tuple(map(int, pos.split(", ")))
    vel: Vector = tuple(map(int, vel.split(", ")))
    return pos, vel


def part_one(lines: Iterable[str]) -> int:
    position_velocity_pairs = []
    for line in lines:
        xyz, vxyz = parse(line)
        position_velocity_pairs.append((xyz[:-1], vxyz[:-1]))

    # Hack to have example and test use parameters that aren't in the input
    if len(position_velocity_pairs) == PART_ONE_EXAMPLE.count("\n"):
        lower, upper = PART_ONE_EXAMPLE_TEST_AREA
    else:
        lower, upper = PART_ONE_TEST_AREA

    intersections = [
        (*pv0, *pv1, *find_intersection(*pv0, *pv1))
        for pv0, pv1 in combinations(position_velocity_pairs, 2)
    ]

    total = 0
    for xy0, v0, xy1, v1, x, y, t0, t1 in intersections:
        # print(f"(x0,y0)={xy0} (vx0,vy0)={v0} (x1,y1)={xy1} (vx1,vy1)={v1}")
        # print(f"intersection: (x,y)=({x},{y}) at t0={t0}, t1={t1}")
        # print()
        if x is None or y is None or t0 is None or t1 is None:
            # Parallel lines
            # print("Parallel lines")
            continue
        elif t0 < 0 or t1 < 0:
            # Intersection is at negative time
            # print("Negative time")
            continue
        elif not (lower <= x <= upper and lower <= y <= upper):
            # Intersection is outside bounds
            # print("Outside bounds")
            continue
        # print("Good intersection")
        total += 1

    return total


def part_two(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    return -1
