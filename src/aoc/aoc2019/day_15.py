#!/usr/bin/env python
"""
PART 1
Use Intcode to solve a maze.
Find len of shortest path to destination.

PART 2
"""
from collections import deque
from collections.abc import Iterable

from aoc.util import Pt, add
from aoc.aoc2019.intcode import Intcode

PART_ONE_EXAMPLE = """\
"""
PART_ONE_EXAMPLE_RESULT = None
PART_ONE_RESULT = 300
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 312


INSTRUCTION_DIRECTION = {
    1: (0, -1),
    2: (0, 1),
    3: (-1, 0),
    4: (1, 0),
}


def walk(
    program: Iterable[int], stop_early: bool
) -> tuple[Pt, set[Pt], tuple[int, ...]]:
    # queue: (current position, instructions to get here)
    queue: deque[tuple[Pt, tuple[int, ...]]] = deque([((0, 0), ())])

    # visited: set of points that some robot has visited
    visited = set()

    # walls: set of points that are walls
    walls = set()

    oxygen_pt = (0, 0)

    while queue:
        # Pop a robot off the stack
        # Look in each direction
        # - If someone else has visited, can't go there
        # - Else, make a new robot, feed it the same path + the one new step
        # - Check the robot's output.
        # -- If it's a wall, can't go there
        # -- If it's the destination, return your instruction sequence (part 1 only)
        # -- Else, onto the queue you go

        pt, instructions = queue.popleft()

        if pt in visited:
            continue
        visited.add(pt)

        for new_instruction, new_direction in INSTRUCTION_DIRECTION.items():
            new_pt = add(pt, new_direction)
            if new_pt in visited or new_pt in walls:
                continue
            # Make a new robot
            robot = Intcode(program)
            # Give it all the same instructions to get here
            for i in instructions:
                robot.run(i)
            # Take the next step
            robot.run(new_instruction)
            result = robot.outputs[-1]
            if result == 0:
                # Wall. Invalid move.
                walls.add(new_pt)
                continue
            # Valid move
            new_instructions = (*instructions, new_instruction)
            if result == 2:
                if stop_early:
                    return new_pt, walls, new_instructions
                else:
                    oxygen_pt = new_pt
                    queue.append((new_pt, new_instructions))
            elif result == 1:
                # Add instructions to the queue
                queue.append((new_pt, new_instructions))
            else:
                raise RuntimeError(f"Unknown robot result: {result}")
    return oxygen_pt, walls, ()


def part_one(lines: Iterable[str]) -> int:
    program = tuple(int(i) for i in "".join(lines).split(","))

    _, _, instructions = walk(program, stop_early=True)
    return len(instructions)


def part_two(lines: Iterable[str]) -> int:
    program = tuple(int(i) for i in "".join(lines).split(","))

    o2_pt, walls, _ = walk(program, stop_early=False)

    # Flood fill from o2_pt
    queue = deque([(0, o2_pt)])
    visited = set()
    steps = 0
    while queue:
        steps, pt = queue.popleft()
        if pt in visited:
            continue
        visited.add(pt)

        for direction in INSTRUCTION_DIRECTION.values():
            new_pt = add(pt, direction)
            if new_pt in visited or new_pt in walls:
                continue
            queue.append((steps + 1, new_pt))
    return steps
