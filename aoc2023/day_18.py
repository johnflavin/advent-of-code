#!/usr/bin/env python
"""

PART 1
Start by digging a 1 cu. m trench.
The instructions give you a relative direction and distance to move.
(And a color hex code, but that is ignored for part 1.)
Dig out a shape, then fill in the dug out area.
Return the area.

PART 2
The "colors" are actually the directions and distances.
First five hex digits are distance.
Last hex digit is color,
0: R, 1: D, 2: L, 3: U
"""

import logging
from collections.abc import Iterable
from enum import Enum


PART_ONE_EXAMPLE = """\
R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)
"""
PART_ONE_EXAMPLE_RESULT = 62
PART_ONE_RESULT = 46334
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 952408144115
PART_TWO_RESULT = 102000662718092


log = logging.getLogger(__name__)


class Direction(Enum):
    U = (-1, 0)
    L = (0, -1)
    D = (1, 0)
    R = (0, 1)


ENCODED_DIRS = (Direction.R, Direction.D, Direction.L, Direction.U)


def parse_line(line: str, is_part_two: bool = False) -> tuple[Direction, int]:
    dir_str, step_length_str, color_str = line.split()
    if is_part_two:
        return ENCODED_DIRS[int(color_str[-2])], int(color_str[2:-2], 16)
    else:
        return Direction[dir_str], int(step_length_str)


def dig_out_a_hole(directions: tuple[tuple[Direction, int], ...]) -> int:
    is_debug = log.isEnabledFor(logging.DEBUG)

    start = (0, 0)
    vertices = [start]
    for direction, step_length in directions:
        last_vertex = vertices[-1]
        next_vertex = (
            last_vertex[0] + direction.value[0] * step_length,
            last_vertex[1] + direction.value[1] * step_length,
        )
        if next_vertex == start:
            break
        vertices.append(next_vertex)
    if len(vertices) % 2 != 0:
        raise RuntimeError(
            "We didn't end back at the start like I thought we would\n" f"{vertices=}"
        )
    if is_debug:
        log.debug(f"raw vertices {vertices}")

    # Assume that vertices will come in pairs on each row,
    # and everything in between the pairs on a row is filled.
    #   (But be careful, because there may be multiple pairs on any given row.)
    # We continue filling in rows like this until we encounter a pair on a
    #   different row. That will cancel one or more of the vertices on our current row.
    # We continue in this way, filling everything in between the pairs we have, until
    # everything is canceled out.
    total = 0
    pairs = []
    left_pair_idx = {}
    right_pair_idx = {}

    sorted_vertices = list(sorted(vertices))
    for (new_l_row, new_l), (new_r_row, new_r) in zip(
        sorted_vertices[::2], sorted_vertices[1::2]
    ):
        if is_debug:
            log.debug(f"{new_l_row=} {new_l=} {new_r_row=} {new_r=}")
        assert new_l_row == new_r_row
        new_row = new_l_row
        del new_l_row
        del new_r_row

        # We want to match a few cases:
        # 1. Left and right cols are in left and right maps, resp.
        #    (May need to assert that they are at the same index).
        #    This means we have found the bottom of a rectangular section.
        # 2. Left (resp. right) col is in left (right) map, but right (left)
        #    col is not in right (left) map. This means we are moving a
        #    point over.
        # 3. Left and right are both in the right and left maps, resp.
        #    This means we are removing a notch.
        #    Combine the outer l,r of the pairs into a new pair.
        # 4. Left (resp. right) is in the right (left) map, but the other is not.
        #    This means we are moving a left (right) point further left (right).
        # 5. Neither l nor r are in any maps.
        #    We're adding a new notch.
        #    Check if it is between any existing pair (negative notch) or just
        #    out on its own (positive notch)
        if new_l in left_pair_idx and new_r in right_pair_idx:
            old_l_idx = left_pair_idx.pop(new_l)
            old_r_idx = right_pair_idx.pop(new_r)
            assert old_l_idx == old_r_idx
            old_row, old_l, old_r = pairs.pop(old_l_idx)

            left_pair_idx = {val: idx for idx, (_, val, _) in enumerate(pairs)}
            right_pair_idx = {val: idx for idx, (_, _, val) in enumerate(pairs)}

            # Fill in the area of this rectangle
            area = (new_row - old_row + 1) * (new_r - new_l + 1)
            if is_debug:
                log.debug(
                    f"Rectangle bottom: {area=} "
                    f"{old_row=} {old_l=} {old_r=} "
                    f"{new_row=} {new_l=} {new_r=} "
                )
            total += area
        elif new_l in left_pair_idx:
            # Move a left point in to the right
            if is_debug:
                log.debug("Move left point right")
                log.debug(f" + before {left_pair_idx=}")
                log.debug(f" + before {right_pair_idx=}")
                log.debug(f" + before {pairs=}")

            old_l_idx = left_pair_idx.pop(new_l)
            old_row, old_l, old_r = pairs[old_l_idx]

            # Fill in the area of the big rectangle above
            total += (new_row - old_row) * (old_r - old_l + 1)

            # Fill in the moved part on this row
            total += new_r - new_l

            # Add the new pair back at the same index
            pairs[old_l_idx] = (new_row, new_r, old_r)
            left_pair_idx[new_r] = old_l_idx

            if is_debug:
                log.debug(f" + after {left_pair_idx=}")
                log.debug(f" + after {right_pair_idx=}")
                log.debug(f" + after {pairs=}")
        elif new_r in right_pair_idx:
            # Move a right point in to the left
            if is_debug:
                log.debug("Move right point left")
                log.debug(f" + before {left_pair_idx=}")
                log.debug(f" + before {right_pair_idx=}")
                log.debug(f" + before {pairs=}")

            old_r_idx = right_pair_idx.pop(new_r)
            old_row, old_l, old_r = pairs[old_r_idx]

            # Fill in the area of the rectangle above
            total += (new_row - old_row) * (old_r - old_l + 1)

            # Fill in the moved part on this row
            total += new_r - new_l

            # Add the new pair back at the same index
            pairs[old_r_idx] = (new_row, old_l, new_l)
            right_pair_idx[new_l] = old_r_idx

            if is_debug:
                log.debug(f" + after {left_pair_idx=}")
                log.debug(f" + after {right_pair_idx=}")
                log.debug(f" + after {pairs=}")

        elif new_l in right_pair_idx and new_r in left_pair_idx:
            # Bottom of a negative notch
            if is_debug:
                log.debug("Negative notch bottom")
                log.debug(f" + before {left_pair_idx=}")
                log.debug(f" + before {right_pair_idx=}")
                log.debug(f" + before {pairs=}")

            # Fill in two rectangles above, move row down, keep old l and r
            old_l_idx = right_pair_idx.pop(new_l)
            old_l_row, old_ll, old_lr = pairs[old_l_idx]
            old_r_idx = left_pair_idx.pop(new_r)
            old_r_row, old_rl, old_rr = pairs[old_r_idx]

            if is_debug:
                log.debug(f" + Popped left pair ({old_l_row}, {old_ll}, {old_lr})")
                log.debug(f" + Popped right pair ({old_r_row}, {old_rl}, {old_rr})")

            # Add left rectangle area
            total += (new_row - old_l_row) * (old_lr - old_ll + 1)

            # Add right rectangle area
            total += (new_row - old_r_row) * (old_rr - old_rl + 1)

            # Add back new top at one of the old indexes, remove other
            pairs[old_l_idx] = (new_row, old_ll, old_rr)

            del pairs[old_r_idx]
            left_pair_idx = {val: idx for idx, (_, val, _) in enumerate(pairs)}
            right_pair_idx = {val: idx for idx, (_, _, val) in enumerate(pairs)}

            if is_debug:
                log.debug(f" + after {left_pair_idx=}")
                log.debug(f" + after {right_pair_idx=}")
                log.debug(f" + after {pairs=}")

        elif new_l in right_pair_idx:
            # Move a right point out to the right
            if is_debug:
                log.debug("Move right point right")
                log.debug(f" + before {left_pair_idx=}")
                log.debug(f" + before {right_pair_idx=}")
                log.debug(f" + before {pairs=}")

            old_r_idx = right_pair_idx.pop(new_l)
            old_row, old_l, old_r = pairs[old_r_idx]

            # Fill in the area of the big rectangle above
            total += (new_row - old_row) * (old_r - old_l + 1)

            # Add the new pair back at the same index
            pairs[old_r_idx] = (new_row, old_l, new_r)
            right_pair_idx[new_r] = old_r_idx

            if is_debug:
                log.debug(f" + after {left_pair_idx=}")
                log.debug(f" + after {right_pair_idx=}")
                log.debug(f" + after {pairs=}")
        elif new_r in left_pair_idx:
            # Move a left point out to the left
            if is_debug:
                log.debug("Move left point left")
                log.debug(f" + before {left_pair_idx=}")
                log.debug(f" + before {right_pair_idx=}")
                log.debug(f" + before {pairs=}")

            old_l_idx = left_pair_idx.pop(new_r)
            old_row, old_l, old_r = pairs[old_l_idx]

            # Fill in the area of the rectangle above
            total += (new_row - old_row) * (old_r - old_l + 1)

            # Add the new pair back at the same index
            pairs[old_l_idx] = (new_row, new_l, old_r)
            left_pair_idx[new_l] = old_l_idx

            if is_debug:
                log.debug(f" + after {left_pair_idx=}")
                log.debug(f" + after {right_pair_idx=}")
                log.debug(f" + after {pairs=}")

        else:
            # Check if we are at the top of a negative notch or a positive notch
            log.debug("Checking top of notch")
            for old_pair_idx, (old_row, old_l, old_r) in enumerate(list(pairs)):
                if old_l is not None and old_l < new_l and old_r > new_r:
                    # Negative notch
                    if is_debug:
                        log.debug("Top of negative notch")
                        log.debug(f" + before {left_pair_idx=}")
                        log.debug(f" + before {right_pair_idx=}")
                        log.debug(f" + before {pairs=}")

                    # Fill in the rectangle above plus the row between the new pair
                    total += (new_row - old_row) * (old_r - old_l + 1)
                    total += new_r - new_l - 1

                    # Break old pair into two new pairs
                    pairs[old_pair_idx] = (new_row, old_l, new_l)
                    left_pair_idx[old_l] = old_pair_idx
                    right_pair_idx[new_l] = old_pair_idx

                    pairs.append((new_row, new_r, old_r))
                    left_pair_idx[new_r] = len(pairs) - 1
                    right_pair_idx[old_r] = len(pairs) - 1

                    # Exit loop
                    if is_debug:
                        log.debug(f" + after {left_pair_idx=}")
                        log.debug(f" + after {right_pair_idx=}")
                        log.debug(f" + after {pairs=}")
                    break
            else:
                # Positive notch. We will fill it in at the bottom.
                if is_debug:
                    log.debug("Top of positive notch")
                    log.debug(f" + before {left_pair_idx=}")
                    log.debug(f" + before {right_pair_idx=}")
                    log.debug(f" + before {pairs=}")

                # Add a new pair
                new_pair = (new_row, new_l, new_r)
                pairs.append(new_pair)
                left_pair_idx[new_l] = len(pairs) - 1
                right_pair_idx[new_r] = len(pairs) - 1

                if is_debug:
                    log.debug(f" + after {left_pair_idx=}")
                    log.debug(f" + after {right_pair_idx=}")
                    log.debug(f" + after {pairs=}")

    return total


def part_one(lines: Iterable[str]) -> int:
    directions = tuple(map(parse_line, lines))
    return dig_out_a_hole(directions)


def part_two(lines: Iterable[str]) -> int:
    directions = tuple(parse_line(line, is_part_two=True) for line in lines)
    return dig_out_a_hole(directions)
