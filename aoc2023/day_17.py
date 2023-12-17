#!/usr/bin/env python
"""

PART 1
Find lowest-cost path from top left to bottom right.
(Don't include cost of top left unless you "enter" it.)
Don't make more than three consecutive moves in same direction.

PART 2
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
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None


log = logging.getLogger(__name__)

# 0 N, 1 W, 2 S, 3 E
STEPS = (0, 1, 2, 3)
STEP_VECS = (
    (-1, 0),
    (0, -1),
    (1, 0),
    (0, 1),
)
DBG_STEP = (
    "N",
    "W",
    "S",
    "E",
    "-",
)


def find_lowest_cost_path(heatmap: tuple[tuple[int, ...], ...]) -> int:
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
    visited: set[tuple[int, int, int, int]] = set()
    while heap:
        heuristic, heat, pt_row, pt_col, step_idx, step_count = heapq.heappop(heap)

        # Have we been here?
        visit = (pt_row, pt_col, step_idx, step_count)
        if visit in visited:
            if is_debug:
                log.debug(
                    f" + Already visited {pt_row}, {pt_col} "
                    f"via {DBG_STEP[step_idx]}({step_count})"
                )
            continue

        # We have been here
        visited.add(visit)
        if is_debug:
            log.debug(
                f" + Visiting {pt_row}, {pt_col} via "
                f"{DBG_STEP[step_idx]}({step_count}) "
                f"{heuristic=}"
            )

        # Are we there yet?
        if pt_row == target_row and pt_col == target_col:
            if is_debug:
                log.debug("~~ Found target ~~")
            target_heat = heat
            break

        # Find possible next moves
        next_step_deltas = [1, 0, -1]
        for next_step_delta in next_step_deltas:
            next_step_idx = (step_idx + next_step_delta) % 4
            if is_debug:
                log.debug(f" ++ Examining next step {DBG_STEP[next_step_idx]}")

            next_step_count = 1 if next_step_delta else step_count + 1
            if next_step_count > 3:
                if is_debug:
                    log.debug(" +++ too many steps")
                continue
            next_step_vec = STEP_VECS[next_step_idx]
            next_pt_row = pt_row + next_step_vec[0]
            next_pt_col = pt_col + next_step_vec[1]

            if not (-1 < next_pt_row < num_rows and -1 < next_pt_col < num_cols):
                if is_debug:
                    log.debug(f" +++ pt {next_pt_row}, {next_pt_col} out of bounds")
                continue

            next_heat = heat + heatmap[next_pt_row][next_pt_col]
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
                    next_step_idx,
                    next_step_count,
                ),
            )

    return target_heat


def part_one(lines: Iterable[str]) -> int:
    weights = tuple(tuple(map(int, line)) for line in lines if line)
    return find_lowest_cost_path(weights)


def part_two(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    return -1
