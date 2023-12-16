#!/usr/bin/env python
r"""

PART 1
Beam of light starts in the top left, heading to the right.
.s are empty space
\s are left-down and right-up mirrors
/s are left-up and right-down mirrors
| and - are splitters. If the beam comes in the flat side it splits to the
    two ends. If it comes in the end nothing happens.
Beams can pass through other beams.
How many spaces are energized?

PART 2
Try starting from every edge position. What is the max energy?

Note: I will need to cache parts of the path to make this feasible.
Switching to a recursive algo might work.
I put in a point and heading, it returns all the points it visits after that.
Edge case: wall. That one is easy.
But how do I do tell if I've visited a location before?
    I need to know where to cut off a path if I've already visited this point in this direction.
    With just the point I am on now, it doesn't seem like there is any memory.
Maybe I have to build the cache myself? Like, when I step recursively I could put
    a placeholder value like None or -1 into the cache.
    That way if I encounter it again later in the journey, I can know that I should
    stop there and not continue.
"""

import logging
from .util import Coord
from collections import deque
from collections.abc import Iterable


PART_ONE_EXAMPLE = r"""
.|...\....
|.-.\.....
.....|-...
........|.
..........
.........\
..../.\\..
.-.-/..|..
.|....-|.\
..//.|....
"""
PART_ONE_EXAMPLE_RESULT = 46
PART_ONE_RESULT = 6921
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 51
PART_TWO_RESULT = None

log = logging.getLogger(__name__)


PosHeading = tuple[Coord, int]


# Heading = 0 north, 1 west, 2 south, 3 east
heading_vecs = [(-1, 0), (0, -1), (1, 0), (0, 1)]
heading_dbg = ["N", "W", "S", "E"]


def walk(
    spaces: list[str],
    start: PosHeading = ((0, 0), 3),
    visited: dict[PosHeading, int] = None,
) -> int:
    num_rows = len(spaces)
    num_cols = len(spaces[0])
    walls = ((-1, num_rows), (-1, num_cols))

    # set of tuples of visited spaces + headings
    visited = visited or {}
    to_visit: deque[PosHeading] = deque((start,))

    # queue of spaces to visit
    while to_visit:
        visit_key = to_visit.popleft()
        space, heading = visit_key
        log.debug(f"Visiting {space} going {heading_dbg[heading]}")

        # Mark that we've been here,
        # but we don't know how many spaces we will see from here
        visited[visit_key] = -1

        heading_dir = heading_vecs[heading]

        # What is in this space?
        # print(space[0], space[1], heading)
        symbol = spaces[space[0]][space[1]]

        # Determine where we head next based on the symbol
        potential_next_steps = []
        if (
            symbol == "."
            or symbol == "-"
            and heading % 2
            or symbol == "|"
            and not heading % 2
        ):
            log.debug("Pass through")
            next_space = (space[0] + heading_dir[0], space[1] + heading_dir[1])
            potential_next_steps.append((next_space, heading))
        elif symbol == "|":
            log.debug("Split ns")
            potential_next_steps.append(((space[0] - 1, space[1]), 0))
            potential_next_steps.append(((space[0] + 1, space[1]), 2))
        elif symbol == "-":
            log.debug("Split ew")
            potential_next_steps.append(((space[0], space[1] - 1), 1))
            potential_next_steps.append(((space[0], space[1] + 1), 3))
        else:
            # mirror
            # \ type
            #   north -> west, west -> north, south -> east, east -> south
            #    (-heading + 1) % 4 == [1, 0, 3, 2]
            # / type
            #   north -> east, west -> south, south -> west, east -> north
            #   (-heading - 1) % 4 == [3, 2, 1, 0]
            new_heading = (-heading + (-1 if symbol == "/" else +1)) % 4
            log.debug(
                f"Reflect: heading {heading_dbg[heading]} -> {heading_dbg[new_heading]}"
            )
            new_heading_vec = heading_vecs[new_heading]
            potential_next_steps.append(
                (
                    (space[0] + new_heading_vec[0], space[1] + new_heading_vec[1]),
                    new_heading,
                )
            )

        # Visit next spaces
        num_spaces_visited_from_here = 0
        for next_visit_key in potential_next_steps:
            next_space, next_heading = next_visit_key
            dir_idx = next_heading % 2
            if next_visit_key in visited:
                # We've already been in this space heading this direction
                # Don't need to do it again
                log.debug(f"We've already done {next_space} going {next_heading}")
                continue
            elif next_space[dir_idx] in walls[dir_idx]:
                # This step would lead us into a wall
                log.debug(f"Hit a wall at {next_space}")
                continue
            to_visit.append((next_space, next_heading))

    # Sum up number of coords we've visited (regardless of heading)
    visited_spaces = set(map(lambda tup: tup[0], visited))
    if log.isEnabledFor(logging.DEBUG):
        # Debug map
        for row_idx in range(num_rows):
            log.debug(
                "".join(
                    "#" if (row_idx, col_idx) in visited_spaces else "."
                    for col_idx in range(num_cols)
                )
            )
    return len(visited_spaces)


def part_one(lines: Iterable[str]) -> int:
    return walk(list(lines))


def part_two(lines: Iterable[str]) -> int:
    spaces = list(lines)
    num_rows = len(spaces)
    num_cols = len(spaces[0])

    starts = []
    for col in range(num_cols):
        starts.append(((0, col), 2))
        starts.append(((num_rows - 1, col), 0))
    for row in range(num_rows):
        starts.append(((row, 0), 3))
        starts.append(((row, num_cols - 1), 1))
    return max(walk(spaces, start=start) for start in starts)
