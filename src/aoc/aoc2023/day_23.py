#!/usr/bin/env python
"""

PART 1
Given a path. Start in the top left, end on the bottom right.
Any slopes must be traversed in the direction they point.
What is the longest path?

PART 2
Ignore slopes
"""
import logging
from collections import defaultdict
from collections.abc import Iterable

from aoc.util import Pt, neighbors, add


PART_ONE_EXAMPLE = """\
#.#####################
#.......#########...###
#######.#########.#.###
###.....#.>.>.###.#.###
###v#####.#v#.###.#.###
###.>...#.#.#.....#...#
###v###.#.#.#########.#
###...#.#.#.......#...#
#####.#.#.#######.#.###
#.....#.#.#.......#...#
#.#####.#.#.#########v#
#.#...#...#...###...>.#
#.#.#v#######v###.###v#
#...#.>.#...>.>.#.###.#
#####v#.#.###v#.#.###.#
#.....#...#...#.#.#...#
#.#########.###.#.#.###
#...###...#...#...#.###
###.###.#.###v#####v###
#...#...#.#.>.>.#.>.###
#.###.###.#.###.#.#v###
#.....###...###...#...#
#####################.#
"""
PART_ONE_EXAMPLE_RESULT = 94
PART_ONE_RESULT = 2182
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 154
PART_TWO_RESULT = 6670


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)

type Slopes = dict[Pt, Pt]

SLOPES = ("^", "<", "v", ">")
OFFSETS_BY_SLOPE = {"^": (0, -1), "<": (-1, 0), "v": (0, 1), ">": (1, 0)}
NO_SLOPE = (0, 0)


def parse_lines(lines: Iterable[str]) -> tuple[Pt, Pt, set[Pt], Slopes]:
    walls = set()
    slopes = {}
    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch == "#":
                walls.add((x, y))
            elif ch in SLOPES:
                slopes[(x, y)] = OFFSETS_BY_SLOPE[ch]
            elif y == 0 and ch == ".":
                start = (x, y)
                walls.add((x, y - 1))
    # Go through last line again to find end
    for x, ch in enumerate(line):
        if ch == ".":
            end = (x, y)
            walls.add((x, y + 1))
    return start, end, walls, slopes


def walk(start: Pt, end: Pt, walls: set[Pt], slopes: Slopes) -> int:
    """
    Here's what we want to do.
    Build a small graph of start, end, and "branch points":
    points with more than two non-wall neighbors.
    Once we build that we do a simple walk to find paths from start to end.

    Building that smaller graph is the main task.
    We have an outer queue over branch points (initialized to "start").
    When we pop a branch point off the queue, we initialize an inner queue
    to the neighbors of the branch point.
    We walk until we get to another branch point or hit a slope we can't climb.
    We store a map of maps. The outer key is the branch point. The inner key
    is the branch point neighbor, the value is a tuple of the ending branch point
    and the length of the path between neighbor and end point (inclusive), or
    if we hit a wall the value should be None, -1.

    So that's three layers of loop:
    1. Branch points
    2. First neighbors
    3. The segment between branch points
    """

    graph = defaultdict(dict)

    visited_branches = set()
    branch_pt_queue = [start]
    while branch_pt_queue:

        # This is a branch point.
        # Try walking down each of its neighbors.
        bp = branch_pt_queue.pop()
        bp_neighbors = [
            n
            for n in neighbors(bp)
            if (
                n not in walls  # No walls
                and n not in visited_branches  # No redos
                and (
                    (bpslope := slopes.get(bp, NO_SLOPE)) == NO_SLOPE
                    or n == add(bp, bpslope)
                )
                and (
                    (nslope := slopes.get(n, NO_SLOPE)) == NO_SLOPE
                    or bp != add(n, nslope)
                )
            )
        ]

        # Traverse each branch
        while bp_neighbors:
            bpn = bp_neighbors.pop()
            if bpn in visited_branches:
                continue
            visited_branches.add(bpn)
            log.debug("Branch %s->%s", bp, bpn)

            seg_visited = {bp}
            seg_queue = [bpn]
            while seg_queue:
                pt = seg_queue.pop()

                if pt in seg_visited:
                    continue
                seg_visited.add(pt)
                log.debug(" + %s", pt)

                ptns = [
                    n
                    for n in neighbors(pt)
                    if (
                        n not in walls  # No walls
                        and n not in seg_visited  # No backtracking
                    )
                ]
                num_n = len(ptns)
                if num_n > 1 or num_n == 0 and pt == end:
                    # We've reached a branch point

                    # End this segment
                    lsv = len(seg_visited) - 1
                    log.debug("Recording %s->%s->%s %d", bp, bpn, pt, lsv)
                    graph[bp][bpn] = (pt, lsv)

                    if pt != end:
                        # Queue the branch point
                        branch_pt_queue.append(pt)
                else:
                    # This is not a branch point
                    traversable = [
                        n
                        for n in ptns
                        if (
                            (
                                (pt_slope := slopes.get(pt, NO_SLOPE)) == NO_SLOPE
                                or n == add(pt, pt_slope)
                            )
                            and (
                                (n_slope := slopes.get(n, NO_SLOPE)) == NO_SLOPE
                                or pt != add(n, n_slope)
                            )
                        )
                    ]
                    if len(traversable) == 1:
                        # No choice at all. Keep walking.
                        seg_queue.append(traversable[0])
                    else:
                        log.debug("Dead end", bp, bpn, pt)
            log.debug("Branch %s->%s finished", bp, bpn)
        log.debug("Branch pt %s finished", bp)

    # We have massively simplified the graph down to only the branch points.
    # Now construct all the valid paths from the segments
    log.debug("Finding path lens")
    paths = []
    queue = [(0, start, frozenset())]
    while queue:
        path_len, seg_start, visited = queue.pop()
        if seg_start in visited:
            continue
        visited = visited | {seg_start}
        for _, (seg_end, seg_len) in graph[seg_start].items():
            new_len = path_len + seg_len
            if seg_end == end:
                log.debug("Found end. Path len %d - %s", new_len, visited)
                paths.append(new_len)
            else:
                queue.append((new_len, seg_end, visited))

    return max(paths)


def find_max_path_len(lines: Iterable[str], ignore_slopes=False) -> int:
    start, end, walls, slopes = parse_lines(lines)
    slopes = {} if ignore_slopes else slopes
    return walk(start, end, walls, slopes)


def part_one(lines: Iterable[str]) -> int:
    return find_max_path_len(lines)


def part_two(lines: Iterable[str]) -> int:
    return find_max_path_len(lines, ignore_slopes=True)
