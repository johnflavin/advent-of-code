#!/usr/bin/env python
"""

PART 1
We are given a map with empty space "." and galaxies "#".
First, any rows and columns with no galaxies should be double width.
Next, find the distance of a shortest grid path between every pair of galaxies.
Answer is sum of all those distances.

Discussion
Find coords of all galaxies.
While parsing for galaxies, keep track of rows and cols that are empty.
Create offset tables by accumulating empty rows/cols.
"Expand" space by adding entry in offset table at
    index row/col to row/col.

Find distances with pairwise differences.

PART 2
"""

from collections.abc import Iterable
from itertools import accumulate, combinations, starmap


PART_ONE_EXAMPLE = """\
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
"""
PART_ONE_EXAMPLE_RESULT = 374
PART_ONE_RESULT = 10154062
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None


Coord = tuple[int, int]


def parse(lines: Iterable[str]) -> list[Coord]:
    # Find galaxies
    coords = []
    unoccupied_rows = []
    unoccupied_cols = None
    for row, line in enumerate(lines):
        unoccupied_cols = unoccupied_cols or [1] * len(line)
        unoccupied_row = 1
        for col, ch in enumerate(line):
            if ch == "#":
                coords.append((row, col))
                unoccupied_row = 0
                unoccupied_cols[col] = 0
        unoccupied_rows.append(unoccupied_row)

    # print("Pre-expansion")
    # print("coords", coords)

    # Expand space
    row_offsets = list(accumulate(unoccupied_rows))
    col_offsets = list(accumulate(unoccupied_cols))
    # print("row offsets", row_offsets)
    # print("col offsets", col_offsets)

    coords = [(row + row_offsets[row], col + col_offsets[col]) for row, col in coords]
    # print("Post expansion")
    # print("coords", coords)
    return coords


def distance(coord1: Coord, coord2: Coord) -> int:
    return abs(coord2[0] - coord1[0]) + abs(coord2[1] - coord1[1])


def part_one(lines: Iterable[str]) -> int:
    coords = parse(lines)
    return sum(starmap(distance, combinations(coords, 2)))


def part_two(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    return -1
