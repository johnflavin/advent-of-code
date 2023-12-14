#!/usr/bin/env python
"""

PART 1
Given a map of round rocks "O", cube rocks "#", and empty spaces ".".
We will tilt the map "north". All the round rocks will roll as far as they can.
They stop when they hit the top edge or another rock (round or cube).

Calculate the "load" of a rock as its row index, starting from 1 at the bottom.
Sum all the row indexes.

PART 2
One "cycle" is tilting the map north, west, south, then east.
What is the total after 1e9 cycles?
"""

from collections.abc import Iterable
from typing import overload


PART_ONE_EXAMPLE = """\
O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....
"""
PART_ONE_EXAMPLE_RESULT = 136
PART_ONE_RESULT = 105784
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 64
PART_TWO_RESULT = 91286


class Rock:
    row: int
    col: int

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __repr__(self):
        return f"{self} {self.row} {self.col}"

    def load(self, max_load: int) -> int:
        return max_load - self.row

    def __eq__(self, other):
        return (
            isinstance(self, type(other))
            and self.row == other.row
            and self.col == other.col
        )


class Rolling(Rock):
    def __str__(self):
        return "O"


class Cube(Rock):
    def __str__(self):
        return "#"

    def load(self, max_load: int) -> int:
        return 0


Rocks = list[Rock]


class RockField:
    rocks: list[Rocks]
    num_rows: int
    num_cols: int

    def __init__(self, num_rows: int, num_cols: int):
        self.rocks = [[] for _ in range(num_cols)]
        self.num_rows = num_rows
        self.num_cols = num_cols

    def __iter__(self):
        return self.rocks.__iter__()

    def __len__(self):
        return self.rocks.__len__()

    @overload
    def __getitem__(self, item: int) -> Rocks:
        pass

    @overload
    def __getitem__(self, item: tuple[int, int]) -> Rock:
        pass

    def __getitem__(self, *item):
        col = self.rocks.__getitem__(item[0])
        if len(item) == 2:
            return col[item[1]]
        else:
            return col

    def __setitem__(self, key, value):
        if isinstance(key, tuple) and isinstance(value, Rock):
            self.rocks.__getitem__(key[0]).__setitem__(key[1], value)
        else:
            self.rocks.__setitem__(key, value)

    def __eq__(self, other):
        return isinstance(other, RockField) and self.rocks.__eq__(other.rocks)

    def __str__(self):
        row_str_lists = [["."] * self.num_cols for _ in range(self.num_rows)]
        # print(self.num_rows, "x", self.num_cols)
        for rocks in self.rocks:
            for rock in rocks:
                # print(repr(rock))
                row_str_lists[rock.row][rock.col] = str(rock)
        return "\n".join("".join(row_str_list) for row_str_list in row_str_lists)

    @property
    def total(self):
        max_load = self.num_rows
        return sum(rock.load(max_load) for rocks in self.rocks for rock in rocks)
        # total = 0
        # max_load = self.num_rows
        # print(f"{max_load=}")
        # for rocks in self.rocks:
        #     for rock in rocks:
        #         rock_load = rock.load(max_load)
        #         total += rock_load
        #         print(repr(rock), rock_load, total)
        #
        # return total

    def rock_iter(self):
        for rocks in self.rocks:
            for rock in rocks:
                if isinstance(rock, Rolling):
                    yield rock.row, rock.col


def fill_line(line: str, row_idx: int, rock_field: RockField):
    for col_idx, (ch, rocks) in enumerate(zip(line, rock_field)):
        if ch == "O":
            rocks.append(Rolling(row_idx, col_idx))
        elif ch == "#":
            rocks.append(Cube(row_idx, col_idx))


def parse(lines: Iterable[str]) -> RockField:
    """Parse input into a row-wise list. Each entry is a column.
    Each column contains a deque of Rocks, filled by appending
    (on the right) starting from the northernmost row."""
    lines = iter(lines)
    line = next(lines)
    rock_field = RockField(0, num_cols=len(line))
    row_idx = 0
    fill_line(line, row_idx, rock_field)
    for row_idx, line in enumerate(lines, 1):
        fill_line(line, row_idx, rock_field)

    rock_field.num_rows = row_idx + 1
    return rock_field


def move_rocks_north_south(rock_field: RockField, north: bool = True) -> RockField:
    default_row = -1 if north else rock_field.num_rows
    offset = 1 if north else -1
    for col_idx, rock_col in enumerate(rock_field):
        moved_rock_col = []
        for rock in rock_col if north else reversed(rock_col):
            if isinstance(rock, Rolling):
                # This rock will move as far "north", toward 0,
                #   or "south", towards num_rows, as it can
                # It will be stopped by whatever is on top of the moved_rocks queue
                # This rock's new rock will be the blocker's
                #   row + 1 if north or -1 if south
                blocker = moved_rock_col[-1] if moved_rock_col else None
                blocker_row = blocker.row if blocker is not None else default_row
                rock.row = blocker_row + offset

            moved_rock_col.append(rock)
        rock_field[col_idx] = (
            moved_rock_col if north else list(reversed(moved_rock_col))
        )

    return rock_field


def move_rocks_north(rock_field: RockField) -> RockField:
    return move_rocks_north_south(rock_field, True)


def move_rocks_south(rock_field: RockField) -> RockField:
    return move_rocks_north_south(rock_field, False)


def move_rocks_east_west(rock_field: RockField, west: bool = True) -> RockField:
    default_col = -1 if west else rock_field.num_cols
    offset = 1 if west else -1

    moved_rows = [[] for _ in range(rock_field.num_rows)]
    for rock_col in rock_field if west else reversed(rock_field):
        for rock in rock_col:
            moved_by_row = moved_rows[rock.row]
            if isinstance(rock, Rolling):
                # This rock will move as far "west", toward 0,
                #   or "east", towards num_cols, as it can
                # It will be stopped by whatever is on top of the moved_rocks queue
                # This rock's new rock will be the blocker's
                #   col + 1 if west or -1 if east
                blocker = moved_by_row[-1] if moved_by_row else None
                blocker_col = blocker.col if blocker is not None else default_col
                rock.col = blocker_col + offset

            moved_by_row.append(rock)
        # rock_field[col_idx] = moved_rocks if west else list(reversed(moved_rocks))

    # Transpose moved_rows onto columnar rock_field
    moved_cols = [[] for _ in range(rock_field.num_rows)]
    for moved_by_row in moved_rows:
        for rock in moved_by_row:
            moved_cols[rock.col].append(rock)

    rock_field.rocks = moved_cols
    return rock_field


def move_rocks_east(rock_field: RockField) -> RockField:
    return move_rocks_east_west(rock_field, False)


def move_rocks_west(rock_field: RockField) -> RockField:
    return move_rocks_east_west(rock_field, True)


def cycle(rock_field: RockField) -> RockField:
    # print("++ move north ++")
    rock_field = move_rocks_north(rock_field)
    # print(rock_field)
    # print("++ move west ++")
    rock_field = move_rocks_west(rock_field)
    # print(rock_field)
    # print("++ move south ++")
    rock_field = move_rocks_south(rock_field)
    # print(rock_field)
    # print("++ move east ++")
    rock_field = move_rocks_east(rock_field)
    # print(rock_field)
    return rock_field


def load(rocks: Rocks, max_row_idx: int):
    max_load = max_row_idx + 1
    return sum(max_load - rock.row for rock in rocks if isinstance(rock, Rolling))


def part_one(lines: Iterable[str]) -> int:
    rock_field = parse(lines)
    # print(rock_field)
    # print("++ move ++")
    rock_field = move_rocks_north(rock_field)
    # print(rock_field)
    # print(f"++ total = {rock_field.total}")
    return rock_field.total


def part_two(lines: Iterable[str]) -> int:
    max_cycle_idx = int(1e9)
    rock_field = parse(lines)
    # print(rock_field)
    previous_rock_iters = [list(rock_field.rock_iter())]
    cycle_len = -1
    cycle_phase = -1
    target_mod_cycle_idx = -1
    for cycle_idx in range(1, max_cycle_idx):
        rock_field = cycle(rock_field)
        # if cycle_idx < 11:
        #     print(f"Cycles: {cycle_idx}")
        #     print(rock_field)
        #     print("+++")
        if cycle_len == -1 and cycle_phase == -1 and target_mod_cycle_idx == -1:
            for previous_cycle_idx, previous_rock_iter in enumerate(
                previous_rock_iters
            ):
                if all(
                    rock == previous_rock
                    for rock, previous_rock in zip(
                        rock_field.rock_iter(), previous_rock_iter
                    )
                ):
                    cycle_phase = previous_cycle_idx
                    cycle_len = cycle_idx - previous_cycle_idx
                    target_mod_cycle_idx = max_cycle_idx % cycle_len
                    # print(f"{cycle_idx} is identical to {previous_cycle_idx}: "
                    #       f"cycle length = {cycle_len} "
                    #       f"target idx = {target_mod_cycle_idx}")
                    break
            else:
                previous_rock_iters.append(list(rock_field.rock_iter()))
                continue
        else:
            mod_cycle_idx = cycle_idx % cycle_len
            # print(f"Cycle {cycle_idx} is equivalent to cycle {mod_cycle_idx}")
            if mod_cycle_idx == target_mod_cycle_idx:
                return rock_field.total
            # else:
            #     print(f"total={rock_field.total}")

    return -1
