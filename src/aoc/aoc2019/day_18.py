#!/usr/bin/env python
"""
PART 1
Navigate a BFS with keys and locks.

PART 2
"""
import logging
import string
from collections import deque
from collections.abc import Iterable

from aoc.util import Pt, neighbors, diags


PART_ONE_EXAMPLE = """\
#################
#i.G..c...e..H.p#
########.########
#j.A..b...f..D.o#
########@########
#k.E..a...g..B.n#
########.########
#l.F..d...h..C.m#
#################
"""
PART_ONE_EXAMPLE_RESULT = 136
PART_ONE_RESULT = 2796
PART_TWO_EXAMPLE = """\
#######
#a.#Cd#
##...##
##.@.##
##...##
#cB#Ab#
#######
"""
PART_TWO_EXAMPLE_RESULT = 8
PART_TWO_RESULT = 1642


log = logging.getLogger(__name__)


def part_one(lines: Iterable[str]) -> int:
    start: Pt = (0, 0)
    keys: dict[Pt, str] = {}
    locks: dict[Pt, str] = {}
    walls: set[Pt] = set()

    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == "#":
                walls.add((x, y))
            elif c in string.ascii_lowercase:
                keys[(x, y)] = c
            elif c in string.ascii_uppercase:
                locks[(x, y)] = c
            elif c == "@":
                start = (x, y)

    num_keys = len(keys)

    # visited: K (pt, set(keys)), V: steps
    visited = {}
    # queue: steps, pt, acquired_keys
    queue = deque([(0, start, frozenset())])
    while queue:
        steps, pt, acquired_keys = queue.popleft()

        v_key = (pt, acquired_keys)
        if (v_steps := visited.get(v_key)) is not None and v_steps <= steps:
            # Been here before in fewer steps
            continue
        visited[v_key] = steps

        # Are we done?
        if len(acquired_keys) == num_keys:
            return steps

        # Where to next?
        n_steps = steps + 1
        for n in neighbors(pt):
            if n in walls:
                # Can't walk into walls
                continue
            if (lock := locks.get(n)) is not None and lock.lower() not in acquired_keys:
                # We haven't opened this lock yet
                continue

            if (
                n_v_steps := visited.get((n, acquired_keys))
            ) is not None and n_v_steps <= n_steps:
                # Don't retrace steps
                continue

            # Looks like a valid destination
            # Did we acquire another key?
            if (n_key := keys.get(n)) is not None:
                n_acquired_keys = acquired_keys | {n_key}
            else:
                n_acquired_keys = acquired_keys
            queue.append((n_steps, n, n_acquired_keys))

    return -1


def part_two(lines: Iterable[str]) -> int:
    starts: list[Pt] = []
    keys: dict[Pt, str] = {}
    locks: dict[Pt, str] = {}
    walls: set[Pt] = set()

    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            if c == "#":
                walls.add((x, y))
            elif c in string.ascii_lowercase:
                keys[(x, y)] = c
            elif c in string.ascii_uppercase:
                locks[(x, y)] = c
            elif c == "@":
                walls.add((x, y))
                walls.update(neighbors((x, y)))
                starts = list(diags((x, y)))

    num_keys = len(keys)

    # visited: K (pts, set(keys)), V: steps
    visited = {(pt, frozenset()): 0 for pt in starts[1:]}
    # queue: total_steps, moved_idx, steps, pts, acquired_keys
    queue = deque([(0, 0, [0] * 4, starts, frozenset())])
    while queue:
        total_steps, moved_idx, steps, pts, acquired_keys = queue.popleft()

        v_key = (pts[moved_idx], acquired_keys)
        if (v_steps := visited.get(v_key)) is not None and v_steps <= steps[moved_idx]:
            # Been here before in fewer steps
            continue
        visited[v_key] = steps[moved_idx]

        # Are we done?
        if len(acquired_keys) == num_keys:
            return total_steps

        # Where to next?
        new_total_steps = total_steps + 1
        for next_move_idx in range(len(pts)):
            # log.info("Moving pt %d", pt_idx)
            new_steps = list(steps)
            new_steps[next_move_idx] += 1
            for n in neighbors(pts[next_move_idx]):
                # log.info("Pt %d neighbor %s", pt_idx, n)
                if n in walls:
                    # Can't walk into walls
                    # log.info(" + Wall")
                    continue

                if (
                    lock := locks.get(n)
                ) is not None and lock.lower() not in acquired_keys:
                    # We haven't opened this lock yet
                    # log.info(" + Locked")
                    continue

                new_pts = list(pts)
                new_pts[next_move_idx] = n
                new_visited_key = (n, acquired_keys)
                if (
                    new_steps_v := visited.get(new_visited_key)
                ) is not None and new_steps_v <= new_steps[next_move_idx]:
                    # Don't retrace steps
                    # log.info(" + Already visited")
                    continue

                # Looks like a valid destination
                # Did we acquire another key?
                if (new_key := keys.get(n)) is not None:
                    new_acquired_keys = acquired_keys | {new_key}
                    # log.info(" + Unlocked %s", new_key)
                else:
                    new_acquired_keys = acquired_keys

                queue.append(
                    (
                        new_total_steps,
                        next_move_idx,
                        new_steps,
                        new_pts,
                        new_acquired_keys,
                    )
                )
    return -1
