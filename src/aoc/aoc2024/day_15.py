#!/usr/bin/env python
"""
PART 1
Given a warehouse map containing walls, boxes, and a robot,
 plus a sequence of moves the robot will attempt to make.
The robot can push boxes, but neither the robot nor boxes can move into walls.
Follow the sequence of moves and calculate the sum of
100y + x for all the boxes.

PART 2
Now we have to expand the map. Boxes take up two spaces in a row.
"""
import logging
from collections.abc import Iterable

from aoc.util import Coord, add


PART_ONE_EXAMPLE = """\
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
"""
PART_ONE_EXAMPLE_RESULT = 10092
PART_ONE_RESULT = 1441031
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
# PART_TWO_EXAMPLE = """\
# #######
# #...#.#
# #.....#
# #..OO@#
# #..O..#
# #.....#
# #######
#
# <vv<<^^<<^^
# """
PART_TWO_EXAMPLE_RESULT = 9021
PART_TWO_RESULT = 1425169


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


type Robot = Coord
type Box = Coord
type Boxes = set[Box]
type Walls = set[Coord]
type Move = Coord
type Moves = tuple[Move, ...]

move_map: dict[str, Coord] = {
    ">": (1, 0),
    "<": (-1, 0),
    "^": (0, -1),
    "v": (0, 1),
}
rev_move_map: dict[Coord, str] = {
    (1, 0): ">",
    (-1, 0): "<",
    (0, -1): "^",
    (0, 1): "v",
}


def parse(
    lines: Iterable[str], part1: bool = True
) -> tuple[Robot, Boxes, Walls, Moves]:
    # Parse the map until we hit a blank line
    robot = (-1, -1)
    boxes = set()
    walls = set()

    for y, line in enumerate(lines):
        if not line:
            break
        for x, ch in enumerate(line):
            if ch == "#":
                walls.add((x, y))
            elif ch == "O":
                boxes.add((x, y))
            elif ch == "@":
                robot = (x, y)

    moves = tuple(move_map[ch] for ch in "".join(lines))

    return robot, boxes, walls, moves


def parse2(lines: Iterable[str]) -> tuple[Robot, Boxes, Boxes, Walls, Moves]:

    robot = (-1, -1)
    lboxes = set()
    rboxes = set()
    walls = set()
    for y, line in enumerate(lines):
        if not line:
            break
        for x, ch in enumerate(line):
            if ch == "#":
                walls.add((2 * x, y))
                walls.add((2 * x + 1, y))
            elif ch == "O":
                lboxes.add((2 * x, y))
                rboxes.add((2 * x + 1, y))
            elif ch == "@":
                robot = (2 * x, y)

    moves = tuple(move_map[ch] for ch in "".join(lines))

    return robot, lboxes, rboxes, walls, moves


def move_part1(
    robot: Robot, boxes: Boxes, walls: Walls, move: Move
) -> tuple[Robot, Boxes]:
    new_robot = add(robot, move)

    if new_robot in walls:
        # Can't move into a wall
        return robot, boxes

    if new_robot not in boxes:
        # Empty space, no problem
        return new_robot, boxes

    # We know the robot has moved into a box.
    # Find the end of the box chain.
    pos = new_robot
    while pos in boxes:
        pos = add(pos, move)
    # We know that pos is not a box right now.
    # If it is empty, the move succeeds.
    # If it is wall, the move fails.
    if pos in walls:
        return robot, boxes
    else:
        # Move succeeds.
        # Move the first and last boxes in the chain.
        boxes.remove(new_robot)
        boxes.add(pos)
        return new_robot, boxes


def move_box(
    lbox: Box, rbox: Box, lboxes: Boxes, rboxes: Boxes, walls: Walls, move: Move
) -> tuple[bool, Boxes, Boxes, Boxes, Boxes]:
    """Check if this big box can move.
    Return four sets: coords to add to and remove from the left boxes,
    and add to and remove from the right boxes"""
    new_lbox = add(lbox, move)
    new_rbox = add(rbox, move)

    def try_move(
        next_lbox: Box, next_rbox: Box
    ) -> tuple[bool, Boxes, Boxes, Boxes, Boxes]:
        # Try to push next box in chain
        did_move, add_l, rem_l, add_r, rem_r = move_box(
            next_lbox, next_rbox, lboxes, rboxes, walls, move
        )

        # If that one moved, this one can move too
        if did_move:
            add_l.add(new_lbox)
            rem_l.add(lbox)
            add_r.add(new_rbox)
            rem_r.add(rbox)
        return did_move, add_l, rem_l, add_r, rem_r

    # Wall?
    if new_lbox in walls or new_rbox in walls:
        # Can't move into a wall
        return False, set(), set(), set(), set()

    # Empty space?
    if (
        move == (1, 0)
        and new_rbox not in lboxes  # Right
        or move == (-1, 0)
        and new_lbox not in rboxes  # Left
        or move[0] == 0
        and all(
            box not in boxes
            for box in (new_lbox, new_rbox)
            for boxes in (lboxes, rboxes)
        )
    ):
        # Empty space, no problem
        return True, {new_lbox}, {lbox}, {new_rbox}, {rbox}

    # We know there is a box in the way
    # Moving Right/left?
    if move[1] == 0 and new_lbox in rboxes and new_rbox in lboxes:
        # Find the edges of the next box in the chain
        next_lbox = add(new_lbox, move)
        next_rbox = add(new_rbox, move)

        # Try to push next box in chain
        return try_move(next_lbox, next_rbox)

    # Moving Up/down in line with box?
    if move[0] == 0 and new_lbox in lboxes and new_rbox in rboxes:
        # Our proposed move is right on top of next box
        next_lbox = new_lbox
        next_rbox = new_rbox

        # Try to push next box in chain
        return try_move(next_lbox, next_rbox)

    # Moving Up/down but diagonal to box?
    if move[0] == 0 and new_lbox in rboxes or new_rbox in lboxes:
        # Case 1: single box, our left -> their right
        if new_lbox in rboxes and new_rbox not in lboxes:
            next_rbox = new_lbox
            next_lbox = add(next_rbox, (-1, 0))
            return try_move(next_lbox, next_rbox)
        # Case 2: single box, our right -> their left
        elif new_rbox in lboxes and new_lbox not in rboxes:
            next_lbox = new_rbox
            next_rbox = add(next_lbox, (1, 0))
            return try_move(next_lbox, next_rbox)
        # Case 3: two boxes
        else:
            l_rbox = new_lbox
            l_lbox = add(l_rbox, (-1, 0))
            l_did_move, l_add_l, l_rem_l, l_add_r, l_rem_r = try_move(l_lbox, l_rbox)
            if not l_did_move:
                return False, set(), set(), set(), set()
            r_lbox = new_rbox
            r_rbox = add(r_lbox, (1, 0))
            r_did_move, r_add_l, r_rem_l, r_add_r, r_rem_r = try_move(r_lbox, r_rbox)
            if not r_did_move:
                return False, set(), set(), set(), set()
            # Both boxes moved. Combine all the moves and return.
            return (
                True,
                {*l_add_l, *r_add_l},
                {*l_rem_l, *r_rem_l},
                {*l_add_r, *r_add_r},
                {*l_rem_r, *r_rem_r},
            )

    raise RuntimeError(f"Missed a case: {move=} {lbox=} {rbox=} {lboxes=} {rboxes=}")


def move_part2(
    robot: Robot, lboxes: Boxes, rboxes: Boxes, walls: Walls, move: Move
) -> tuple[Robot, Boxes, Boxes]:
    new_robot = add(robot, move)

    if new_robot in walls:
        # Can't move into a wall
        return robot, lboxes, rboxes

    if new_robot not in lboxes and new_robot not in rboxes:
        # Empty space, no problem
        return new_robot, lboxes, rboxes

    # We know the robot has moved into a box.
    # find left and right edge of the box
    if new_robot in lboxes:
        lbox = new_robot
        rbox = add(lbox, (1, 0))
    else:
        rbox = new_robot
        lbox = add(rbox, (-1, 0))

    # Attempt to move the box (and any boxes it moves into)
    did_move, add_l, rem_l, add_r, rem_r = move_box(
        lbox, rbox, lboxes, rboxes, walls, move
    )

    if did_move:
        # Do the adds and removes, except skip redundant moves
        #  where a box moved into the space of another box
        lboxes.difference_update(rem_l - add_l)
        rboxes.difference_update(rem_r - add_r)
        lboxes.update(add_l - rem_l)
        rboxes.update(add_r - rem_r)
        return new_robot, lboxes, rboxes
    else:
        # No move
        return robot, lboxes, rboxes


def part_one(lines: Iterable[str]) -> int:
    robot, boxes, walls, moves = parse(lines)

    for move in moves:
        robot, boxes = move_part1(robot, boxes, walls, move)

    return sum(100 * y + x for x, y in boxes)


def part_two(lines: Iterable[str]) -> int:
    robot, lboxes, rboxes, walls, moves = parse2(lines)

    max_x, max_y = 0, 0  # Only need these if we are debugging

    def debug_log_map():
        for y in range(max_y):
            s = "".join(
                (
                    "#"
                    if pt in walls
                    else (
                        "["
                        if pt in lboxes
                        else "]" if pt in rboxes else "@" if pt == robot else "."
                    )
                )
                for x in range(max_x)
                if (pt := (x, y))
            )
            log.debug(s)

    if is_debug:
        for x, y in walls:
            if x >= max_x:
                max_x = x + 1
            if y >= max_y:
                max_y = y + 1

        debug_log_map()

    for move in moves:
        robot, lboxes, rboxes = move_part2(robot, lboxes, rboxes, walls, move)
        if is_debug:
            log.debug("move %s", rev_move_map[move])
            debug_log_map()

    return sum(100 * y + x for x, y in lboxes)
