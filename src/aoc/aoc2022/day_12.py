#!/usr/bin/env python
"""
PART 1
Pathfinding time!
Given a map of heights as lowercase letters a-z,
a start S (at height a) and end E (height z),
find the shortest path from S to E given that at each step
the height can increase by at most 1.

PART 2
Find shortest path from any starting point at elevation a

(Note: shortest that actually reaches the end, I guess...)
"""
from collections import deque
from collections.abc import Iterable

from aoc.util import Pt


PART_ONE_EXAMPLE = """\
Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
"""
PART_ONE_EXAMPLE_RESULT = 31
PART_ONE_RESULT = 468
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 29
PART_TWO_RESULT = 459


a = ord("a")


def add(x: Pt, y: Pt) -> Pt:
    return x[0] + y[0], x[1] + y[1]


def walk(start: Pt, end: Pt, grid) -> list[Pt]:
    num_rows = len(grid)
    num_cols = len(grid[0])

    frontier = deque([start])

    # This will allow us to reconstruct the path to the end
    # Values: Previous step in the path and how many steps to get here
    history = {start: (None, 0)}

    while frontier:
        # pt = heapq.heappop(frontier)
        pt = frontier.popleft()
        if pt == end:
            break

        prev_pt, num_steps_to_pt = history[pt]
        for step in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            next_pt = add(pt, step)
            num_steps_to_next_pt = num_steps_to_pt + 1

            # Verify next_pt is on grid
            if not (0 <= next_pt[0] < num_rows and 0 <= next_pt[1] < num_cols):
                continue
            # Verify next_pt is not too tall
            if grid[next_pt[0]][next_pt[1]] > grid[pt[0]][pt[1]] + 1:
                continue
            # Verify we haven't already been there in fewer steps
            if next_pt in history and history[next_pt][1] <= num_steps_to_next_pt:
                continue
            # Next point seems good to me, throw it on the pile
            frontier.append(next_pt)
            history[next_pt] = (pt, num_steps_to_next_pt)

    # Unwind the path, starting from end
    path = []
    pt = end
    while pt in history:
        path.append(pt)
        pt = history[pt][0]
    return path


def part_one(lines: Iterable[str]) -> int:
    grid = []
    start: Pt = (-1, -1)
    end: Pt = (-1, -1)
    for r, line in enumerate(lines):
        if not line:
            continue
        grid_line = []
        for c, ch in enumerate(line):
            if ch == "S":
                start = (r, c)
                ch = "a"
            elif ch == "E":
                end = (r, c)
                ch = "z"
            grid_line.append(ord(ch) - a)
        grid.append(grid_line)

    path = walk(start, end, grid)
    return len(path) - 1


def part_two(lines: Iterable[str]) -> int:
    grid = []
    starts: list[Pt] = []
    end: Pt = (-1, -1)
    for r, line in enumerate(lines):
        if not line:
            continue
        grid_line = []
        for c, ch in enumerate(line):
            if ch == "S":
                ch = "a"
            elif ch == "E":
                end = (r, c)
                ch = "z"
            if ch == "a":
                starts.append((r, c))
            grid_line.append(ord(ch) - a)
        grid.append(grid_line)

    return min(len(path) for start in starts if (path := walk(start, end, grid))) - 1
