#!/usr/bin/env python
"""
PART 1
Given a map of asteroids, find the asteroid position that can "see"
the most other asteroids; return the number it can see.

PART 2
Kill the asteroids in order starting from pointing up and rotating clockwise.
Which will be the 200th asteroid killed?
Answer is 100*x+y
"""
import itertools
import math
from collections import defaultdict
from collections.abc import Iterable

from aoc.util import Pt, sub, manhattan_distance

PART_ONE_EXAMPLE = """\
.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##
"""
PART_ONE_EXAMPLE_RESULT = 210
PART_ONE_RESULT = 319
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 802
PART_TWO_RESULT = 517


def parse(lines: Iterable[str]) -> set[Pt]:
    return {
        (x, y) for y, line in enumerate(lines) for x, c in enumerate(line) if c == "#"
    }


def find_max_visible(asteroids: set[Pt]) -> tuple[Pt, dict[Pt, list[Pt]]]:
    # Find the slope of the line from one asteroid to another
    # For a given a1, only a single a2 can be on that slope.
    # For counting purposes it doesn't matter which.
    # But we do need to be careful to uniquely order them...
    visible_slopes = defaultdict(dict)
    for a1, a2 in itertools.combinations(asteroids, 2):
        a_min = min(a1, a2)
        a_max = max(a1, a2)
        diff = sub(a_max, a_min)
        diff_gcd = math.gcd(diff[0], diff[1])
        smallest_integer_diff = diff[0] // diff_gcd, diff[1] // diff_gcd
        min_dict = visible_slopes[a_min]
        if smallest_integer_diff not in min_dict:
            min_dict[smallest_integer_diff] = []
        min_dict[smallest_integer_diff].append(a_max)

        neg_smallest_integer_diff = -smallest_integer_diff[0], -smallest_integer_diff[1]
        max_dict = visible_slopes[a_max]
        if neg_smallest_integer_diff not in max_dict:
            max_dict[neg_smallest_integer_diff] = []
        max_dict[neg_smallest_integer_diff].append(a_min)

    max_asteroid = (0, 0)
    max_dict = {}
    max_len = 0
    for a, slope_dict in visible_slopes.items():
        if (lsd := len(slope_dict)) > max_len:
            max_asteroid = a
            max_dict = slope_dict
            max_len = lsd

    return max_asteroid, max_dict


def part_one(lines: Iterable[str]) -> int:
    asteroids = parse(lines)
    _, max_dict = find_max_visible(asteroids)
    return len(max_dict)


def part_two(lines: Iterable[str]) -> int:
    asteroids = parse(lines)
    max_asteroid, max_dict = find_max_visible(asteroids)

    # We know we have the location of the maximum asteroid,
    # all the slopes from this asteroid to every other,
    # and keyed under those slopes we have unordered lists
    # of all the asteroids at that slope.
    # Ordering the lists will be easy based on the distance from
    # here to there.
    # (Later note: We reverse this sort order so we can quickly pop off
    #  the closest point.)
    # But we need a way to order the slopes as well,
    # starting at "Up" and proceeding clockwise.
    # I think we split into quadrants, find the slopes in each
    # quadrant by checking signs of x and y, and we order by
    # value of arctan. (Or just the ratio y/x.)
    # NOTE:
    # Pointing "up" and going clockwise in this system where "up" is -Y,
    # is the same as starting from -Y and going CCW in a right-handed
    # coordinate system.
    # That makes it easier because we don't need to break out quadrants,
    # only the +/-X semiplanes and the two points on the +/-Y axis.
    def pt_sort_key(pt: Pt) -> int:
        return manhattan_distance(pt, max_asteroid)

    def slope_sort_key(slope_pts: tuple[Pt, list[Pt]]) -> float:
        slope = slope_pts[0]
        return slope[1] / slope[0]

    up = (0, -1)
    down = (0, 1)
    ordered_slopes = []
    # First add "Up" = -Y axis
    if (up_pts := max_dict.get(up)) is not None:
        ordered_slopes.append((up, sorted(up_pts, key=pt_sort_key, reverse=True)))

    # Then add pts on the +X semiplane
    # QIV: (x, y): (0, -1)->(1, 0), y/x: -inf->0
    # QI: (x, y): (0, 1) -> (1, 0), y/x: 0->inf
    ordered_slopes.extend(
        sorted(
            (
                (slope, sorted(pts, key=pt_sort_key, reverse=True))
                for slope, pts in max_dict.items()
                if 0 < slope[0]
            ),
            key=slope_sort_key,
        )
    )

    # Now add "Down": +Y axis
    if (down_pts := max_dict.get(down)) is not None:
        ordered_slopes.append((down, sorted(down_pts, key=pt_sort_key)))

    # Lastly add points in the -X semiplane
    # QII: (x, y): (0, 1) -> (-1, 0), y/x: -inf->0
    # QIII: (x, y): (-1, 0)->(0, -1), y/x: 0->inf
    ordered_slopes.extend(
        sorted(
            (
                (slope, sorted(pts, key=pt_sort_key, reverse=True))
                for slope, pts in max_dict.items()
                if slope[0] < 0
            ),
            key=slope_sort_key,
        )
    )

    # Now we have everything in some kind of order.
    # But it's a nested order. The slopes are ordered among themselves,
    # and within a slope the points on that line are ordered.
    # How do we go about ordering it in a global way?
    # Visit each slope in turn and pop a point off...
    target_idx = 200
    global_order = []
    while len(global_order) < target_idx:
        for slope, slope_pts in ordered_slopes:
            if len(global_order) >= target_idx:
                break
            if slope_pts:
                global_order.append(slope_pts.pop())
    pt = global_order[-1]
    return 100 * pt[0] + pt[1]
