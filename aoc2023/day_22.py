#!/usr/bin/env python
"""

PART 1
Given a list of brick end positions (x, y, z),
find which bricks are atop others after they've fallen as far as they can.

Bricks can be safely removed if everything atop them is supported by at least
one other brick. (Or if nothing is atop them.)
How many can be safely removed?

PART 2
"""
import logging
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import groupby, product
from typing import Self


PART_ONE_EXAMPLE = """\
1,0,1~1,2,1
0,0,2~2,0,2
0,2,3~2,2,3
0,0,4~0,2,4
2,0,5~2,2,5
0,1,6~2,1,6
1,1,8~1,1,9
"""
PART_ONE_EXAMPLE_RESULT = 5
PART_ONE_RESULT = 495
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None


log = logging.getLogger(__name__)

Vector = tuple[int, int, int]


@dataclass(frozen=True)
class Range:
    lower: int
    upper: int

    def overlaps(self, other) -> bool:
        return self.lower <= other.upper and other.lower <= self.upper

    def __iter__(self):
        return iter(range(self.lower, self.upper + 1))

    def __str__(self):
        if self.lower == self.upper:
            return str(self.lower)
        return f"[{self.lower}, {self.upper}]"

    def __repr__(self):
        return self.__str__()


@dataclass(eq=False)
class Brick:
    x: Range
    y: Range
    z: Range
    above: list[Self] = field(repr=False)
    _below: list[Self] = field(repr=False)

    def __init__(self, line: str):
        left_str, right_str = line.split("~")
        lx, ly, lz = tuple(map(int, left_str.split(",")))
        rx, ry, rz = tuple(map(int, right_str.split(",")))

        self.x = Range(lx, rx)
        self.y = Range(ly, ry)
        self.z = Range(lz, rz)
        self.above = []
        self._below = []

    def overlaps_xy(self, other) -> bool:
        return self.x.overlaps(other.x) or self.y.overlaps(other.y)

    def set_zlower(self, new_lower: int):
        self.z = Range(new_lower, new_lower + self.z.upper - self.z.lower)

    @property
    def below(self):
        return self._below

    @below.setter
    def below(self, below: list[Self]):
        log.debug(f"Setting bricks below to {below}")
        self._below = list(below)
        self.set_zlower(self._below[0].z.upper + 1)
        log.debug(f"Setting z={self.z}")
        for intersecting in self._below:
            log.debug(f"Adding self to {intersecting}.above")
            intersecting.above.append(self)

    @property
    def xy(self):
        return product(self.x, self.y)

    @property
    def z_groups(self):
        return groupby(product(self.x, self.y, self.z), lambda prod: prod[2])

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    # @property
    # def points(self):
    #     return tuple(pt for pt in self)

    # def __iter__(self):
    #     return product(self.x, self.y, self.z)
    #
    # def __iter__(self):
    #     yield self.x
    #     yield self.y
    #     yield self.z


def find_removable(bricks: Iterable[Brick]) -> int:
    log.debug("Checking for removable bricks")
    # return sum(
    #     not brick.above
    #     or all(
    #         any(below_above_brick != brick for below_above_brick in above_brick.below)
    #         for above_brick in brick.above
    #     )
    #     for brick in bricks
    # )
    total = 0
    bricks_to_check = deque(bricks)
    seen = set()
    while bricks_to_check:
        brick = bricks_to_check.popleft()
        if brick in seen:
            continue
        seen.add(brick)
        log.debug(f" + {brick}")
        if not brick.above:
            log.debug(" ++ Removable: none above")
            total += 1
        elif all(
            any(below_above_brick != brick for below_above_brick in above_brick.below)
            for above_brick in brick.above
        ):
            log.debug(
                " ++ Removable: some above but "
                "they all have at least one other below"
            )
            total += 1
        else:
            log.debug(" ++ Not removable")

        bricks_to_check.extend(brick.above)

    return total


def arrange(bricks: Iterable[Brick]) -> tuple[Brick, ...]:
    ceiling = {}
    floor = []
    for brick in bricks:
        # log.debug(f"{brick} {ceiling}")
        # Find what bricks make up the "ceiling" of the xy points of this brick
        intersecting_max_z = []
        for xy in brick.xy:
            log.debug(f"Examining {xy} for {brick}")
            if ceil_brick := ceiling.get(xy):
                log.debug(f"Found {ceil_brick} on ceiling")
                if (
                    not intersecting_max_z
                    or intersecting_max_z[0].z.upper == ceil_brick.z.upper
                ):
                    log.debug(f" + Max height below {ceil_brick.z.upper}")
                    intersecting_max_z.append(ceil_brick)
                elif intersecting_max_z[0].z.upper < ceil_brick.z.upper:
                    log.debug(f" + Max height below {ceil_brick.z.upper}")
                    intersecting_max_z = [ceil_brick]
                else:
                    log.debug(f" + Height {ceil_brick.z.upper} < max height")

        if not intersecting_max_z:
            # Didn't find any bricks below. This one falls to the floor.
            brick.set_zlower(1)
            log.debug(f"Nothing below. Shifted z down. {brick}")
            floor.append(brick)
        else:
            # Set this brick to be just above all the bricks below
            brick.below = intersecting_max_z
            for intersecting in intersecting_max_z:
                intersecting.above.append(brick)

        # Update the ceiling
        ceiling.update(
            {xyz[:2]: brick for _, z_group in brick.z_groups for xyz in z_group}
        )
        # log.debug(f"Updated ceiling:\n{ceiling}")

    return tuple(floor)


def parse(lines: Iterable[str]) -> Iterable[Brick]:
    yield from map(Brick, lines)


def part_one(lines: Iterable[str]) -> int:
    raw_bricks = parse(lines)
    rough_sort = sorted(raw_bricks, key=lambda brick: brick.z.lower)
    arranged = arrange(rough_sort)
    return find_removable(arranged)


def part_two(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    return -1
