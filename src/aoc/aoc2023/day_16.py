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
    I need to know where to cut off a path if I've already visited
    this point in this direction.
    With just the point I am on now, it doesn't seem like there is any memory.
Maybe I have to build the cache myself? Like, when I step recursively I could put
    a placeholder value like None or -1 into the cache.
    That way if I encounter it again later in the journey, I can know that I should
    stop there and not continue.

No, I want to use the built-in cache.
To do that I'll need to only send in cachable args to my new function,
    like the map and my current step.
Specifically, I can't send in the previously visited locations.
So how do I avoid my cachable function looping forever?
Well, if you think about it, only the - and | can cause loops.
You can't have a loop with just the mirrors, because once you get back
    around to a certain point you'd get bounced out.
The mirrors have different behavior in different directions, but it's all symmetric.
You can't come from two different directions and get the same output direction.
But with - and | you can.

What I'll try is breaking the full path into segments.
A segment starts with some input point and heading,
    continues on through the path as before,
    but ends if it hits a wall or a - or | (regardless of direction).
That function then returns a list of all the points it visited, and whatever
    next steps there were (if any).
Then we pop back out to the top-level function and start new segments
    at whatever next steps there were from the last segment.
"""

import logging
from collections.abc import Iterable
from functools import cache

from aoc.util import Coord


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
PART_TWO_RESULT = 7594

log = logging.getLogger(__name__)


PosHeading = tuple[Coord, int]


# Heading = 0 north, 1 west, 2 south, 3 east
heading_vecs = [(-1, 0), (0, -1), (1, 0), (0, 1)]
heading_dbg = ["N", "W", "S", "E"]


@cache
def walk_segment(spaces: tuple[str, ...], walls: tuple[Coord], to_visit: PosHeading):
    """Walk until you get to a - or a |. This is cachable."""

    all_steps = []
    next_steps = [to_visit]
    while len(next_steps) == 1:
        to_visit = next_steps.pop()
        space, heading = to_visit
        log.debug(f"Visiting {space} going {heading_dbg[heading]}")

        all_steps.append(to_visit)

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
            heading_dir = heading_vecs[heading]
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
        elif symbol == "/" or symbol == "\\":
            # mirror
            # \ type
            #   north -> west, west -> north, south -> east, east -> south
            #   (-heading + 1) % 4 == [1, 0, 3, 2]
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

        for next_visit in potential_next_steps:
            next_space, next_heading = next_visit
            dir_idx = next_heading % 2
            if next_space[dir_idx] in walls[dir_idx]:
                # This step would lead us into a wall
                log.debug(f"Hit a wall at {next_space}")
                continue
            next_steps.append(next_visit)

        if symbol == "-" or symbol == "|":
            break

    return tuple(all_steps), tuple(next_steps) if next_steps else None


def walk(
    spaces: tuple[str, ...],
    start: PosHeading = ((0, 0), 3),
) -> int:
    num_rows = len(spaces)
    num_cols = len(spaces[0])
    walls = ((-1, num_rows), (-1, num_cols))

    # set of tuples of visited spaces + headings
    visited = set()
    to_visit_queue = [start]

    # queue of spaces to visit
    while to_visit_queue:
        to_visit = to_visit_queue.pop()
        log.debug(
            f"Beginning segment walk at {to_visit[0]} "
            f"heading {heading_dbg[to_visit[1]]}"
        )
        steps, next_steps = walk_segment(spaces, walls, to_visit)
        log.debug(f"Done with segment walk. Ended at {steps[-1][0]}.")
        visited.update(steps)
        if next_steps:
            for next_step in next_steps:
                if next_step not in visited:
                    to_visit_queue.append(next_step)

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
    spaces = tuple(line for line in lines if line)
    return walk(spaces)


def part_two(lines: Iterable[str]) -> int:
    spaces = tuple(line for line in lines if line)
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
