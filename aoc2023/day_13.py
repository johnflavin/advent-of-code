#!/usr/bin/env python
"""

PART 1
Given groups of patterns. They will either reflect vertically or horizontally
between two columns or rows, resp.

Find the reflections.
Answer is # columns left of all vertical reflections +
    100 * number of rows above horizontal reflections

PART 2

"""

from collections.abc import Iterable, Iterator


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
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None


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


def find_reflection(rows: list[str], row_wise: bool) -> int:
    num_rows = len(rows)
    num_cols = len(rows[0])
    n = num_rows if row_wise else num_cols
    # print("\n".join(rows))
    # print(f"{n=}")
    # row_or_col_str = "row" if row_wise else "col"
    for reflection_idx in range(n - 1):
        # print(f"Trying reflection {row_or_col_str} {reflection_idx}: "
        #       f"range({reflection_idx}, -1, -1) range({reflection_idx + 1}, {n})")
        # print(f"Trying reflection {row_or_col_str} {reflection_idx}")
        for idx1, idx2 in zip(
            range(reflection_idx, -1, -1), range(reflection_idx + 1, n)
        ):
            # print(idx1, idx2)
            if (
                row_wise
                and rows[idx1] != rows[idx2]
                or not row_wise
                and any(rows[row][idx1] != rows[row][idx2] for row in range(num_rows))
            ):
                # print(f"{row_or_col_str} {idx1} != {idx2}")
                break
            # else:
            #     print(f"{row_or_col_str} {idx1} == {idx2}")
        else:
            # print("All succeeded. Found reflection around "
            #       f"{row_or_col_str} {reflection_idx}")
            return reflection_idx + 1
    # print(f"No reflection found {row_or_col_str}-wise")
    return -1


def part_one(lines: Iterable[str]) -> int:
    return sum(
        100 * row_refl
        if (row_refl := find_reflection(rows, row_wise=True)) > -1
        else find_reflection(rows, row_wise=False)
        for rows in parse(lines)
    )


def part_two(lines: Iterable[str]) -> int:
    # thing = (line for line in lines if line)
    return -1
