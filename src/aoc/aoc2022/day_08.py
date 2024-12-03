#!/usr/bin/env python
"""
PART 1
Given a map of tree heights, count how many are "visible" from outside
along a row or column.
"Visible" is defined as all the trees between a given tree and an edge
have lower heights.

PART 2
Find highest "scenic score": product of number of trees visible in each direction
"visible" here means number of trees traversed until reaching
    one of height >= current, or an edge
"""
import logging
import math
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
30373
25512
65332
33549
35390
"""
PART_ONE_EXAMPLE_RESULT = 21
PART_ONE_RESULT = 1840
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 8
PART_TWO_RESULT = None


log = logging.getLogger(__name__)


def part_one(lines: Iterable[str]) -> int:
    def visible(values: Iterable[int]) -> list[bool]:
        """Given sequence of values, is a value greater than all others so far?"""
        max_value = -1
        vis = []
        for value in values:
            is_vis = value > max_value
            vis.append(is_vis)
            if is_vis:
                max_value = value
        return vis

    cols: list[list[int]] = []
    vis_rows: list[list[bool]] = []
    for row_str in lines:
        row = list(map(int, row_str))
        if not row:
            continue
        # Check from left
        vis_left = visible(row)
        # Check from right
        vis_right = visible(reversed(row))
        # Visibility along this row
        vis_rows.append(
            [left | right for left, right in zip(vis_left, reversed(vis_right))]
        )
        # Stick row entries into columns
        if not cols:
            cols = [[] for _ in row]
        for col, r_val in zip(cols, row):
            col.append(r_val)

    # Now check along columns
    vis_cols = []
    for col in cols:
        # Check from top
        vis_top = visible(col)
        # Check from bottom
        vis_bottom = visible(reversed(col))
        # Visibility along this column
        vis_cols.append(
            [top | bottom for top, bottom in zip(vis_top, reversed(vis_bottom))]
        )

    # Combine rows and columns
    log.debug("vis_rows %s", vis_rows)
    log.debug("vis_cols %s", vis_cols)
    return sum(
        vis_rows[row_idx][col_idx] | vis_cols[col_idx][row_idx]
        for row_idx in range(len(vis_rows))
        for col_idx in range(len(vis_cols))
    )


def part_two(lines: Iterable[str]) -> int:
    grid = [[int(r) for r in line] for line in lines if line]
    num_rows = len(grid[0])
    num_cols = len(grid)

    def score_col(row_idx: int, col_idx: int, up: bool) -> int:
        step = 1 if up else -1
        limit = num_cols if up else -1
        val = grid[row_idx][col_idx]
        total = 0
        for idx in range(col_idx + step, limit, step):
            total += 1
            if grid[row_idx][idx] >= val:
                break
        return total

    def score_row(row_idx: int, col_idx: int, up: bool) -> int:
        step = 1 if up else -1
        limit = num_rows if up else -1
        val = grid[row_idx][col_idx]
        total = 0
        for idx in range(row_idx + step, limit, step):
            total += 1
            if grid[idx][col_idx] >= val:
                break
        return total

    def visibility_score(row_idx: int, col_idx: int) -> int:
        # Anything on an edge can see 0 in that direction, so total score is 0
        if (
            row_idx == 0
            or row_idx == num_rows - 1
            or col_idx == 0
            or col_idx == num_cols - 1
        ):
            return 0
        return math.prod(
            f(row_idx, col_idx, up)
            for f in (score_row, score_col)
            for up in (True, False)
        )

    return max(
        visibility_score(row_idx, col_idx)
        for row_idx in range(num_rows)
        for col_idx in range(num_cols)
    )
