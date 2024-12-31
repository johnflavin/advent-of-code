#!/usr/bin/env python
"""
PART 1
Given a map of unoccupied seats (L), apply rules
- If a seat is empty and there are no adjacent occupied seats (incl. diags), occupy it
- If a seat is occupied and four or more adjacent seats are occupied, unoccupy it

Apply rules until nothing changes. How many occupied seats?

PART 2
Rules have changed.
Now instead of looking at adjacent seats, we consider sight lines in each of the
    eight directions, first visible seat wins.
Second rule changes from 4 occupied seats to 5.
Apply rules until nothing changes. How many occupied seats?
"""
import logging
from collections.abc import Iterable

from aoc.util import Pt, neighbors, OFFSETS_WITH_DIAGS, add


PART_ONE_EXAMPLE = """\
L.LL.LL.LL
LLLLLLL.LL
L.L.L..L..
LLLL.LL.LL
L.LL.LL.LL
L.LLLLL.LL
..L.L.....
LLLLLLLLLL
L.LLLLLL.L
L.LLLLL.LL
"""
PART_ONE_EXAMPLE_RESULT = 37
PART_ONE_RESULT = 2359
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 26
PART_TWO_RESULT = 2131

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)

type Coords = set[Pt]


def parse(lines: Iterable[str]) -> tuple[Coords, Coords, int, int]:
    occupied, unoccupied = set(), set()
    max_y, max_x = 0, 0
    for y, line in enumerate(lines):
        if y >= max_y:
            max_y = y + 1
        for x, c in enumerate(line):
            if c == "L":
                unoccupied.add((x, y))
            if x >= max_x:
                max_x = x + 1
    return occupied, unoccupied, max_x, max_y


def debug_draw(o: Coords, u: Coords, max_x: int, max_y: int) -> None:
    if not is_debug:
        return
    for y in range(max_y):
        line = "".join(
            "#" if (pt := (x, y)) in o else "L" if pt in u else "."
            for x in range(max_x)
        )
        log.debug(line)
    log.debug("-" * 5)


def part_one(lines: Iterable[str]) -> int:
    occupied, unoccupied, max_x, max_y = parse(lines)

    def apply_rules(o: Coords, u: Coords) -> tuple[Coords, Coords]:
        # Currently unoccupied, becoming occupied
        uo = {pt for pt in u if all(n not in o for n in neighbors(pt, diags=True))}
        # Currently occupied, becoming occupied
        ou = {pt for pt in o if sum(n in o for n in neighbors(pt, diags=True)) >= 4}

        return o - ou | uo, u - uo | ou

    while (new_ou := apply_rules(occupied, unoccupied)) != (occupied, unoccupied):
        occupied, unoccupied = new_ou
        if is_debug:
            debug_draw(occupied, unoccupied, max_x, max_y)

    return len(occupied)


def part_two(lines: Iterable[str]) -> int:
    occupied, unoccupied, max_x, max_y = parse(lines)

    def inbounds(pt: Pt) -> bool:
        return 0 <= pt[0] < max_x and 0 <= pt[1] < max_y

    def first_seat(pt: Pt, delta: Pt) -> Pt:
        while inbounds(pt := add(pt, delta)):
            if pt in occupied or pt in unoccupied:
                return pt

    def apply_rules(o: Coords, u: Coords) -> tuple[Coords, Coords]:
        # Currently unoccupied, becoming occupied
        uo = {
            pt
            for pt in u
            if all(first_seat(pt, d) not in o for d in OFFSETS_WITH_DIAGS)
        }
        # Currently occupied, becoming occupied
        ou = {
            pt
            for pt in o
            if sum(first_seat(pt, d) in o for d in OFFSETS_WITH_DIAGS) >= 5
        }

        return o - ou | uo, u - uo | ou

    while (new_ou := apply_rules(occupied, unoccupied)) != (occupied, unoccupied):
        occupied, unoccupied = new_ou
        if is_debug:
            debug_draw(occupied, unoccupied, max_x, max_y)

    return len(occupied)
