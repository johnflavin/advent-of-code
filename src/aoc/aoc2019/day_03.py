#!/usr/bin/env python
"""
PART 1
Given two runs of wire, find intersection point closest to 0,0.

PART 2
Find the intersection with the minimum number of total steps
"""
import itertools
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
R75,D30,R83,U83,L12,D49,R71,U7,L72
U62,R66,U55,R34,D71,R55,D58,R83
"""
PART_ONE_EXAMPLE_RESULT = 159
PART_ONE_RESULT = 221
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 610
PART_TWO_RESULT = 18542

type WireSeg = tuple[int, int, int, int]
type WireSegs = tuple[WireSeg, ...]


def parse(line: str) -> tuple[WireSegs, WireSegs]:
    hsegs = []
    vsegs = []
    seg_x, seg_y = (0, 0)
    steps = 0
    for seg in line.split(","):

        extent = int(seg[1:])
        if seg[0] in "RL":
            seg_x_start = seg_x
            seg_x_end = seg_x + extent * (1 if seg[0] == "R" else -1)
            hsegs.append((steps, seg_x_start, seg_x_end, seg_y))
            seg_x = seg_x_end
        else:
            seg_y_start = seg_y
            seg_y_end = seg_y + extent * (1 if seg[0] == "U" else -1)
            vsegs.append((steps, seg_x, seg_y_start, seg_y_end))
            seg_y = seg_y_end

        steps += extent
    return tuple(hsegs), tuple(vsegs)


def part_one(lines: Iterable[str]) -> int:
    line1, line2 = list(lines)
    w1hsegs, w1vsegs = parse(line1)
    w2hsegs, w2vsegs = parse(line2)

    min_intersection = 1 << 10  # Just making up some big value, hope it works
    for (_, w1xstart, w1xend, w1y), (_, w2x, w2ystart, w2yend) in itertools.chain(
        itertools.product(w1hsegs, w2vsegs), itertools.product(w2hsegs, w1vsegs)
    ):
        w1xmin, w1xmax = (w1xstart, w1xend) if w1xstart < w1xend else (w1xend, w1xstart)
        w2ymin, w2ymax = (w2ystart, w2yend) if w2ystart < w2yend else (w2yend, w2ystart)
        if w1xmin <= w2x <= w1xmax and w2ymin <= w1y <= w2ymax:
            intersection_distance = abs(w2x) + abs(w1y)
            if 0 < intersection_distance < min_intersection:
                min_intersection = intersection_distance

    return min_intersection


def part_two(lines: Iterable[str]) -> int:
    line1, line2 = list(lines)
    w1hsegs, w1vsegs = parse(line1)
    w2hsegs, w2vsegs = parse(line2)

    min_steps = 1 << 20  # Just making up some big value, hope it works
    for (w1steps, w1xstart, w1xend, w1y), (
        w2steps,
        w2x,
        w2ystart,
        w2yend,
    ) in itertools.chain(
        itertools.product(w1hsegs, w2vsegs), itertools.product(w2hsegs, w1vsegs)
    ):
        w1xmin, w1xmax = (w1xstart, w1xend) if w1xstart < w1xend else (w1xend, w1xstart)
        w2ymin, w2ymax = (w2ystart, w2yend) if w2ystart < w2yend else (w2yend, w2ystart)
        if w1xmin <= w2x <= w1xmax and w2ymin <= w1y <= w2ymax:
            # We have an intersection, and we know how many steps it took to get
            # to the beginning of this segment for each wire.
            # Now calc steps from beginning of seg to intersection
            w1segsteps = abs(w2x - w1xstart)
            w2segsteps = abs(w1y - w2ystart)
            total_steps = w1steps + w1segsteps + w2steps + w2segsteps
            if 0 < total_steps < min_steps:
                min_steps = total_steps

    return min_steps
