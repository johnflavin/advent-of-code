#!/usr/bin/env python
"""
You start in the top left position,
your destination is the bottom right position,
and you cannot move diagonally.
The number at each position is its risk level;
to determine the total risk of an entire path,
add up the risk levels of each position you enter
(that is, don't count the risk level of your starting position unless you enter it;
leaving it adds no risk to your total).

Your goal is to find a path with the lowest total risk.
"""

from collections.abc import Iterable

import networkx

from .day_09 import neighbor_indices


EXAMPLE = """\
1163751742
1381373672
2136511328
3694931569
7463417111
1319128137
1359912421
3125421639
1293138521
2311944581
"""
PART_ONE_EXAMPLE_RESULT = 40
PART_TWO_EXAMPLE_RESULT = 315
PART_ONE_RESULT = 626
PART_TWO_RESULT = 2966


def solution(weights: tuple[tuple[int, ...], ...]) -> int:
    num_rows = len(weights)
    num_cols = len(weights[0])

    graph = networkx.DiGraph()

    # Add an edge going from each neighbor into this point,
    #  weighted by this point's cost
    graph.add_edges_from(
        (neighbor, (row_idx, col_idx), {"weight": weight})
        for row_idx, row in enumerate(weights)
        for col_idx, weight in enumerate(row)
        for neighbor in neighbor_indices((row_idx, col_idx), num_rows, num_cols)
    )

    # Find the shortest (least weighted) path through the graph
    return networkx.shortest_path_length(
        graph, (0, 0), (num_rows - 1, num_cols - 1), "weight"
    )


def part_one(lines: Iterable[str]) -> int:
    weights = tuple(tuple(map(int, line)) for line in lines)
    return solution(weights)


def part_two(lines: Iterable[str]) -> int:
    base_weights = tuple(tuple(map(int, line)) for line in lines)
    base_num_rows = len(base_weights)
    base_num_cols = len(base_weights[0])
    num_rows = base_num_rows * 5
    num_cols = base_num_cols * 5
    weights = [list([0] * num_cols) for _ in range(num_rows)]
    for row in range(num_rows):
        for col in range(num_cols):
            row_tile, base_row = divmod(row, base_num_rows)
            col_tile, base_col = divmod(col, base_num_cols)
            weights[row][col] = (
                base_weights[base_row][base_col] + row_tile + col_tile
            ) % 9 or 9
    weights = tuple(tuple(line) for line in weights)

    return solution(weights)
