#!/usr/bin/env python
"""

PART 1
Given groups of patterns. They will either reflect vertically or horizontally
between two columns or rows, resp.

Find the reflections.
Answer is # columns left of all vertical reflections +
    100 * number of rows above horizontal reflections

PART 2
Each set of inputs has exactly one "smudge",
a single . that should be a # or vice versa.

When the smudge is fixed, a set of inputs that initially failed to reflect
vertically (resp. horizontally) will succeed.

Calculate the answer the same way as before.
"""

from collections.abc import Iterable, Iterator

from aoc.util import Coord


PART_ONE_EXAMPLE = """\
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
"""
PART_ONE_EXAMPLE_RESULT = 405
PART_ONE_RESULT = 37113
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 400
PART_TWO_RESULT = 30449


def parse(lines: Iterable[str]) -> Iterator[list[str]]:
    lines = iter(lines)
    while True:
        rows = []
        try:
            while line := next(lines):
                rows.append(line)
        except StopIteration:
            # print("\n".join(rows))
            yield rows
            break
        if not rows:
            break
        # print("\n".join(rows))
        yield rows
        # print("---")


def flip(row: str, coord: Coord) -> str:
    prefix = row[: coord[1]] if coord[1] > 0 else ""
    entry = "." if row[coord[1]] == "#" else "#"
    suffix = row[coord[1] + 1 :] if coord[1] < len(row) - 1 else ""
    return prefix + entry + suffix


def reflect_about_idx(
    rows: list[str], reflection_idx: int, row_wise: bool, fix_smudge: bool
) -> int:
    # row_or_col_str = "row" if row_wise else "col"
    # print(f"Trying reflection {row_or_col_str} {reflection_idx}")

    num_rows = len(rows)
    num_cols = len(rows[0])
    n = num_rows if row_wise else num_cols

    possible_smudge_coords = []
    for idx1, idx2 in zip(range(reflection_idx, -1, -1), range(reflection_idx + 1, n)):
        # print(idx1, idx2)
        inequalities = (
            [
                ((idx1, col), (idx2, col))
                for col in range(num_cols)
                if rows[idx1][col] != rows[idx2][col]
            ]
            if row_wise
            else [
                ((row, idx1), (row, idx2))
                for row in range(num_rows)
                if rows[row][idx1] != rows[row][idx2]
            ]
        )
        if inequalities:
            # print(f"{row_or_col_str} {idx1} != {idx2}")
            if fix_smudge and len(inequalities) == 1 and not possible_smudge_coords:
                # print("Found possible smudge")
                possible_smudge_coords.append((reflection_idx, inequalities[0]))
            else:
                break
        # else:
        #     print(f"{row_or_col_str} {idx1} == {idx2}")
    else:
        if fix_smudge and len(possible_smudge_coords) == 1:
            reflection_idx, smudge = possible_smudge_coords[0]
            smudge_coord = smudge[0]
            # print(f"We found a smudge: "
            #       f"{smudge} reflecting about {row_or_col_str} {reflection_idx}")
            rows[smudge_coord[0]] = flip(rows[smudge_coord[0]], smudge_coord)
            return reflect_about_idx(rows, reflection_idx, row_wise, fix_smudge=False)
        elif not fix_smudge:
            # print("All succeeded. Found reflection around "
            #       f"{row_or_col_str} {reflection_idx}")
            return (100 if row_wise else 1) * (reflection_idx + 1)

    return -1


def find_reflection(rows: list[str], row_wise: bool, fix_smudge: bool) -> int:
    # print("\n".join(rows))

    for reflection_idx in range((len(rows) if row_wise else len(rows[0])) - 1):
        if (
            attempt := reflect_about_idx(rows, reflection_idx, row_wise, fix_smudge)
        ) > -1:
            return attempt

    return -1


def run_the_thing(lines: Iterable[str], fix_smudge: bool = False) -> int:
    return sum(
        (
            row_refl
            if (row_refl := find_reflection(rows, row_wise=True, fix_smudge=fix_smudge))
            > -1
            else find_reflection(rows, row_wise=False, fix_smudge=fix_smudge)
        )
        for rows in parse(lines)
    )


def part_one(lines: Iterable[str]) -> int:
    return run_the_thing(lines)


def part_two(lines: Iterable[str]) -> int:
    return run_the_thing(lines, fix_smudge=True)
