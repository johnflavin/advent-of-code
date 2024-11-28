#!/usr/bin/env python
"""

PART 1
Find lowest-cost path from top left to bottom right.
(Don't include cost of top left unless you "enter" it.)
Don't make more than three consecutive moves in same direction.

PART 2
Once an ultra crucible starts moving in a direction,
it needs to move a minimum of four blocks in that direction
before it can turn (or even before it can stop at the end).
However, it will eventually start to get wobbly:
an ultra crucible can move a maximum of ten consecutive blocks without turning.
"""

import heapq
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533
"""
PART_ONE_EXAMPLE_RESULT = 102
PART_ONE_RESULT = 1065
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 94
PART_TWO_RESULT = 1249


log = logging.getLogger(__name__)

# 0 N, 1 W, 2 S, 3 E
DIRECTION_VECS = (
    (-1, 0),
    (0, -1),
    (1, 0),
    (0, 1),
)
DBG_DIR = (
    "N",
    "W",
    "S",
    "E",
)


def find_lowest_cost_path(
    heatmap: tuple[tuple[int, ...], ...], is_part_two: bool = False
) -> int:
    is_debug = log.isEnabledFor(logging.DEBUG)

    num_rows = len(heatmap)
    num_cols = len(heatmap[0])

    target_heat = -1
    start_row, start_col = 0, 0
    start_dist = num_rows + num_cols - 2
    target_row, target_col = (num_rows - 1, num_cols - 1)

    heap = []
    heapq.heappush(
        heap,
        (
            start_dist,
            0,
            start_row,
            start_col,
            3,
            0,
        ),
    )
    heapq.heappush(
        heap,
        (
            start_dist,
            0,
            start_row,
            start_col,
            2,
            0,
        ),
    )
    visited: set[tuple[int, int, int, int]] = set()
    while heap:
        heuristic, heat, pt_row, pt_col, dir_idx, dir_count = heapq.heappop(heap)

        # Have we been here?
        visit = (pt_row, pt_col, dir_idx, dir_count)
        if visit in visited:
            if is_debug:
                log.debug(
                    f" + Already visited {pt_row}, {pt_col} "
                    f"via {DBG_DIR[dir_idx]}({dir_count})"
                )
            continue

        # We have been here
        visited.add(visit)
        if is_debug:
            log.debug(
                f" + Visiting {pt_row}, {pt_col} via "
                f"{DBG_DIR[dir_idx]}({dir_count}) "
                f"{heuristic=}"
            )

        # Are we there yet?
        if pt_row == target_row and pt_col == target_col:
            if is_debug:
                log.debug("~~ Found target ~~")
            target_heat = heat
            break

        # Find possible next moves
        next_dir_deltas = [1, 0, -1]
        for next_dir_delta in next_dir_deltas:
            next_dir_idx = (dir_idx + next_dir_delta) % 4
            if is_debug:
                log.debug(f" ++ Examining next direction {DBG_DIR[next_dir_idx]}")

            if is_part_two:
                next_dir_count = 4 if next_dir_delta else max(dir_count + 1, 4)
                next_num_steps = 4 if next_dir_delta else next_dir_count - dir_count
            else:
                next_dir_count = 1 if next_dir_delta else dir_count + 1
                next_num_steps = 1

            if next_dir_count > (3 if not is_part_two else 10):
                if is_debug:
                    log.debug(" +++ too many steps")
                continue
            next_dir_row, next_dir_col = DIRECTION_VECS[next_dir_idx]

            next_pt_row = pt_row + next_dir_row * next_num_steps
            next_pt_col = pt_col + next_dir_col * next_num_steps

            if not (-1 < next_pt_row < num_rows and -1 < next_pt_col < num_cols):
                if is_debug:
                    log.debug(f" +++ pt {next_pt_row}, {next_pt_col} out of bounds")
                continue

            next_heat = heat + sum(
                heatmap[pt_row + next_dir_row * step_i][pt_col + next_dir_col * step_i]
                for step_i in range(1, next_num_steps + 1)
            )
            next_dist = (num_rows - 1 - next_pt_row) + (num_cols - 1 - next_pt_col)
            next_heuristic = next_heat + next_dist

            if is_debug:
                log.debug(f" +++ Pushing next step {next_pt_row}, {next_pt_col}")
            heapq.heappush(
                heap,
                (
                    next_heuristic,
                    next_heat,
                    next_pt_row,
                    next_pt_col,
                    next_dir_idx,
                    next_dir_count,
                ),
            )

    return target_heat


def part_one(lines: Iterable[str]) -> int:
    weights = tuple(tuple(map(int, line)) for line in lines if line)
    return find_lowest_cost_path(weights)


def part_two(lines: Iterable[str]) -> int:
    weights = tuple(tuple(map(int, line)) for line in lines if line)
    return find_lowest_cost_path(weights, is_part_two=True)
