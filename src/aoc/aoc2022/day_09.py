#!/usr/bin/env python
"""
PART 1
We have a rope with a head and a tail.
Tail must be adjacent to head (diag counts).
Start head and tail on same spot.
Given sequence of head moves, count number of positions tail has.

PART 2
Now rope is length 10 instead of length 2.
"""
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

PART_ONE_EXAMPLE = """\
R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
"""
PART_ONE_EXAMPLE_RESULT = 13
PART_ONE_RESULT = 6337
PART_TWO_EXAMPLE = """\
R 5
U 8
L 8
D 3
R 17
D 10
L 25
U 20
"""
PART_TWO_EXAMPLE_RESULT = 36
PART_TWO_RESULT = 2455


log = logging.getLogger(__name__)


@dataclass(frozen=True, repr=False)
class Coord:
    x: int
    y: int

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, other: Self) -> Self:
        return Coord(self.x + other.x, self.y + other.y)

    def __neg__(self) -> Self:
        return Coord(-self.x, -self.y)

    def __sub__(self, other: Self) -> Self:
        return Coord(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"({self.x},{self.y})"


ZERO = Coord(0, 0)

H_MOVE_MAP = {
    "R": Coord(1, 0),
    "L": Coord(-1, 0),
    "U": Coord(0, 1),
    "D": Coord(0, -1),
}


# H-T position diff -> T move
T_MOVE_MAP = {
    # Coincident
    ZERO: ZERO,
    # Adjacent
    Coord(0, 1): ZERO,
    Coord(0, -1): ZERO,
    Coord(1, 0): ZERO,
    Coord(-1, 0): ZERO,
    # Diagonal
    Coord(1, 1): ZERO,
    Coord(1, -1): ZERO,
    Coord(-1, 1): ZERO,
    Coord(-1, -1): ZERO,
    # Non-adjacent: up
    Coord(1, 2): Coord(1, 1),
    Coord(0, 2): Coord(0, 1),
    Coord(-1, 2): Coord(-1, 1),
    # Non-adjacent: down
    Coord(1, -2): Coord(1, -1),
    Coord(0, -2): Coord(0, -1),
    Coord(-1, -2): Coord(-1, -1),
    # Non-adjacent: right
    Coord(2, 1): Coord(1, 1),
    Coord(2, 0): Coord(1, 0),
    Coord(2, -1): Coord(1, -1),
    # Non-adjacent: left
    Coord(-2, 1): Coord(-1, 1),
    Coord(-2, 0): Coord(-1, 0),
    Coord(-2, -1): Coord(-1, -1),
    # Non-adjacent: diagonal
    Coord(2, 2): Coord(1, 1),
    Coord(-2, 2): Coord(-1, 1),
    Coord(2, -2): Coord(1, -1),
    Coord(-2, -2): Coord(-1, -1),
}


def process_move(hmove: Coord, hpos: Coord, tpos: Coord) -> tuple[Coord, Coord]:
    hpos_new: Coord = hpos + hmove
    tpos_hpos_new_diff = hpos_new - tpos
    tmove = T_MOVE_MAP[tpos_hpos_new_diff]
    tpos_new = tpos + Coord(*tmove)
    return hpos_new, tpos_new


def part_one(lines: Iterable[str]) -> int:
    hposes = [Coord(0, 0)]
    tposes = [Coord(0, 0)]
    for line in lines:
        if not line:
            continue
        direction, amount_str = line.split()
        for _ in range(int(amount_str)):
            hmove = H_MOVE_MAP[direction]
            hpos_new = hposes[-1] + hmove
            tmove = T_MOVE_MAP[hpos_new - tposes[-1]]

            hposes.append(hpos_new)
            tposes.append(tposes[-1] + tmove)

    return len(set(tposes))


def part_two(lines: Iterable[str]) -> int:
    rope_len = 10
    pos = [Coord(0, 0)] * rope_len
    log.debug(pos)
    tail_pos = {Coord(0, 0)}
    for line in lines:
        if not line:
            continue
        log.debug(line)
        direction, amount_str = line.split()
        for _ in range(int(amount_str)):
            moves = [H_MOVE_MAP[direction]]
            for h_idx in range(rope_len):
                h_new = pos[h_idx] + moves[-1]
                pos[h_idx] = h_new
                if (t_idx := h_idx + 1) < rope_len:
                    moves.append(T_MOVE_MAP[h_new - pos[t_idx]])
            tail_pos.add(pos[-1])
            log.debug(pos)

    return len(tail_pos)
