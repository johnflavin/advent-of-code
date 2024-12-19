#!/usr/bin/env python
"""
PART 1
Ok, this one is hard to summarize.
Rocks are falling in a chamber 7 units wide.
(I bet the width will change in part 2.)
They fall in a sequence which repeats.
Rock appears with its left edge two units from the left wall,
    bottom edge three units from the highest rock / floor.
The input is a series of left/right movements the rocks will take.
They make one side movement (if possible) then move down (if possible).
Once a down move is no longer possible the rock comes to rest and the next
rock appears.

How tall is the tower after 2022 rocks fall?

PART 2
How tall after 1000000000000 steps?
Which means cycle detection. But I'm not entirely sure how.
"""
import itertools
import logging
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from functools import partial

from aoc.util import Coord

PART_ONE_EXAMPLE = """\
>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>
"""
PART_ONE_EXAMPLE_RESULT = 3068
PART_ONE_RESULT = 3067
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 1514285714288
PART_TWO_RESULT = None


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


def add(a: Coord, b: Coord) -> Coord:
    return a[0] + b[0], a[1] + b[1]


def sub(a: Coord, b: Coord) -> Coord:
    return a[0] - b[0], a[1] - b[1]


@dataclass
class Shape:
    anchor: Coord
    extents: tuple[Coord, ...]

    def __iter__(self):
        for e in self.extents:
            yield add(self.anchor, e)

    def __contains__(self, item: Coord) -> bool:
        return item in set(self)


#
# class FixedSet:
#     n: int
#     s: set
#
#     def __init__(self, n: int, *stuff):
#         self.n = n
#         self.s = set(*stuff)
#
#     def add(self, other):
#         self.s.add(other)
#         self._resize()
#
#     def update(self, others):
#         self.s.update(others)
#         self._resize()
#
#     def _resize(self):
#         while len(self.s) >= self.n:
#             self.s.pop()
#
#     def __contains__(self, item):
#         return item in self.s
#
#     def __iter__(self):
#         yield from self.s


Dash = partial(Shape, extents=((0, 0), (1, 0), (2, 0), (3, 0)))
Plus = partial(Shape, extents=((1, 0), (1, 1), (0, 1), (1, 2), (2, 1)))
El = partial(Shape, extents=((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)))
Pipe = partial(Shape, extents=((0, 0), (0, 1), (0, 2), (0, 3)))
Block = partial(Shape, extents=((0, 0), (0, 1), (1, 0), (1, 1)))
SHAPES = (Dash, Plus, El, Pipe, Block)

type Shape2 = list[int]
Dash2 = [0b0011110]
Plus2 = [0b0001000, 0b0011100, 0b0001000]
El2 = [0b0011100, 0b0000100, 0b0000100]
Pipe2 = [0b0010000, 0b0010000, 0b0010000, 0b0010000]
Block2 = [0b0011000, 0b0011000]
SHAPES2 = (Dash2, Plus2, El2, Pipe2, Block2)

MOVES = {
    ">": (1, 0),
    "<": (-1, 0),
}


def debug_log(rocks: set[Coord], next_shape: Shape, width: int) -> None:
    if not is_debug:
        return
    log.debug("")
    max_y = max(y for x, y in next_shape)
    min_shape_y = min(y for x, y in next_shape)
    rocks_by_height = defaultdict(set)
    for x, y in rocks:
        rocks_by_height[y].add((x, y))
    # log.debug("shape %s", next_shape)
    # log.debug("rocks %s", rocks)
    for y in range(max_y, 0, -1):
        log.debug(
            "|%s|",
            "".join(
                (
                    "@"
                    if y >= min_shape_y and (x, y) in next_shape
                    else "#" if (x, y) in rocks_by_height[y] else "."
                )
                for x in range(width)
            ),
        )
    log.debug("+%s+", "-" * width)


def do_the_thing(
    num_shapes: int,
    jet_seq: str,
    jet_start_idx: int = 0,
    shape_start_idx: int = 0,
    rocks: set[Coord] = None,
) -> int:
    width = 7
    rocks = {(x, 0) for x in range(width)} if rocks is None else rocks

    def in_rocks(s: Shape) -> bool:
        return any(c in rocks for c in s)

    def in_walls(s: Shape) -> bool:
        return not all(0 <= x < width for x, y in s)

    def move(s: Shape, m: Coord) -> bool:
        """Try moving a shape. If it was invalid, undo it.
        Return whether we did the move or not."""
        s.anchor = add(s.anchor, m)
        invalid = in_rocks(s) or in_walls(s)
        if invalid:
            s.anchor = sub(s.anchor, m)
        return not invalid

    jetidxgen = itertools.cycle(range(len(jet_seq)))
    for i in range(jet_start_idx):
        next(jetidxgen)

    for shape_num in range(num_shapes):
        shape_idx = (shape_num + shape_start_idx) % 5
        shape_init = SHAPES[shape_idx]
        shape = shape_init((2, max(y for x, y in rocks) + 4))

        debug_log(rocks, shape, width)

        did_move_down = True
        while did_move_down:
            # Move right/left
            jet_idx = next(jetidxgen)
            _ = move(shape, MOVES[jet_seq[jet_idx]])

            # Move down
            did_move_down = move(shape, (0, -1))

        rocks.update(shape)

    return max(y for x, y in rocks)


def do_the_thing2(
    num_shapes: int,
    jet_seq: str,
    jet_start_idx: int = 0,
    shape_start_idx: int = 0,
    rocks: set[Coord] = None,
) -> int:

    rocks = {0: 0b1111111}

    def in_rocks(s: Shape2, y: int) -> bool:
        return any(c & rocks.get(y + i, 0) for i, c in enumerate(s))

    def move_hits_walls(s: Shape2, left: bool) -> bool:
        """If left, is MSB==1? If not left, is LSB==1?"""
        return any(c >> 6 if left else c & 0b1 for c in s)

    def move(s: Shape2, y: int, left: bool) -> Shape2:
        """If a move doesn't hit the rocks or walls, return the moved shape.
        Else return the shape."""

        if move_hits_walls(s, left):
            return s
        moved = [c << 1 if left else c >> 1 for c in s]
        return s if in_rocks(moved, y) else moved

    jetidxgen = itertools.cycle(range(len(jet_seq)))
    for i in range(jet_start_idx):
        next(jetidxgen)

    max_y = 0
    for shape_num in range(num_shapes):
        shape_idx = (shape_num + shape_start_idx) % 5
        shape = SHAPES[shape_idx]

        y = max_y + 2

        # debug_log(rocks, shape, width)

        did_move_down = True
        while did_move_down:
            # Move right/left
            jet_idx = next(jetidxgen)
            _ = move(shape, y, jet_seq[jet_idx] == "<")

            # Move down
            did_move_down = move(shape, (0, -1))

        rocks.update(shape)

    return max(y for x, y in rocks)


def part_one(lines: Iterable[str]) -> int:
    jet_seq = "".join(lines)
    num_shapes = 2022

    return do_the_thing(num_shapes, jet_seq)


def part_two(lines: Iterable[str]) -> int:
    # jet_seq = "".join(lines)
    # num_shapes = 1000000000000
    #
    # width = 7
    # rocks = deque([0b1111111])
    #
    # def move(s: Shape, m: Coord) -> bool:
    #     """Try moving a shape. If it was invalid, undo it.
    #     Return whether we did the move or not."""
    #     s.anchor = add(s.anchor, m)
    #     valid = all(0 <= x < width and (x, y) not in rocks for x, y in s)
    #
    #     if not valid:
    #         s.anchor = sub(s.anchor, m)
    #     return valid
    #
    # def prune(r: set[Coord]) -> tuple[set[Coord], frozenset[Coord], int]:
    #     max_y = max(y for x, y in r)
    #     pruned_r = {(x, y) for x, y in r if y >= max_y - 8}
    #     min_y = min(y for x, y in pruned_r)
    #     relative_r = frozenset((x, y-min_y) for x, y in pruned_r)
    #     return pruned_r, relative_r, max_y
    #
    # jetidxgen = itertools.cycle(range(len(jet_seq)))
    # cycle_detection = {}
    # for shape_num in range(num_shapes):
    #     shape_idx = shape_num % 5
    #     shape_init = SHAPES[shape_idx]
    #     shape = shape_init((2, max(y for x, y in rocks) + 4))
    #
    #     # debug_log(rocks, shape, width)
    #
    #     did_move_down = True
    #     jet_idx = 0
    #     while did_move_down:
    #         # Move right/left
    #         jet_idx = next(jetidxgen)
    #         _ = move(shape, MOVES[jet_seq[jet_idx]])
    #
    #         # Move down
    #         did_move_down = move(shape, (0, -1))
    #
    #     rocks.update(shape)
    #     rocks, relative_height_rocks, height = prune(rocks)
    #     state = (shape_idx, jet_idx, relative_height_rocks)
    #     if shape_num % 10000 == 0 and log.isEnabledFor(logging.DEBUG):
    #         log.debug("shape_num=%d state=%s", shape_num, state)
    #         log.debug("rocks=%s", rocks)
    #     (previous_shape_num, previous_height) = cycle_detection.get(state, (-1, -1))
    #     if previous_height > -1:
    #         log.info(
    #             "Cycle: shape %d height %d is the same as shape %d height %d",
    #             previous_shape_num,
    #             previous_height,
    #             shape_num,
    #             height
    #         )
    #         cycle_len = shape_num - previous_shape_num
    #         num_cycles, shapes_remaining = divmod(
    #             num_shapes - previous_shape_num, cycle_len
    #         )
    #         return do_the_thing(shapes_remaining, jet_seq, jet_idx, shape_idx, rocks)
    #     cycle_detection[state] = shape_num, height
    return -1
