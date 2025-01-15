#!/usr/bin/env python
"""
PART 1
3d gravity simulation
Get some planet positions, implement a basic gravity.
Calculate an "energy" standin as the answer.

PART 2
How many steps before it repeats?
"""
import math
import re
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
<x=-8, y=-10, z=0>
<x=5, y=5, z=10>
<x=2, y=-7, z=3>
<x=9, y=-8, z=-3>
"""
PART_ONE_EXAMPLE_RESULT = 1940
EXAMPLE_STEPS = 100
STEPS = 1000
PART_ONE_RESULT = 8287
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 4686774924
PART_TWO_RESULT = 528250271633772


INPUT_VEC_RE = re.compile(r"<x=(?P<x>-?\d+), y=(?P<y>-?\d+), z=(?P<z>-?\d+)>")


def parse(lines: Iterable[str]) -> list[list[int]]:
    return [
        [int(m.group(axis)) for axis in "xyz"]
        for line in lines
        if (m := INPUT_VEC_RE.match(line)) is not None
    ]


def step_axis(positions: list[int], velocities: list[int]) -> None:
    num_planets = len(positions)

    # Update velocities
    for planet_idx1 in range(num_planets):
        p1 = positions[planet_idx1]
        for planet_idx2 in range(num_planets):
            if planet_idx1 == planet_idx2:
                continue
            p2 = positions[planet_idx2]
            if p1 < p2:
                velocities[planet_idx1] += 1
            elif p1 > p2:
                velocities[planet_idx1] -= 1
    # Update positions
    for planet_idx in range(num_planets):
        positions[planet_idx] = positions[planet_idx] + velocities[planet_idx]


def find_cycle(pos: list[int], vel: list[int]) -> int:
    """For a given axis, run the simulation until a state repeats.
    Return first repeated step number.

    Note: We assume state 0 is the state that gets repeated.
    I don't think this is true in general but it is true for
    all inputs I've seen in this puzzle, so we'll go with it."""
    state_zero = (*pos, *vel)

    # Take first step so we can actually enter the loop...
    step_axis(pos, vel)
    i = 1

    # Loop until we get back to 0
    while (*pos, *vel) != state_zero:
        step_axis(pos, vel)
        i += 1

    return i


def part_one(lines: Iterable[str]) -> int:
    positions = parse(lines)
    num_planets = len(positions)

    # Break into the axes, operate on them independently
    xs, ys, zs = list(map(list, zip(*positions)))
    vxs, vys, vzs = [0] * num_planets, [0] * num_planets, [0] * num_planets

    steps = EXAMPLE_STEPS if positions[0] == [-8, -10, 0] else STEPS
    for _ in range(steps):
        step_axis(xs, vxs)
        step_axis(ys, vys)
        step_axis(zs, vzs)

    # Return value: Energy
    # Recombine axes into position and velocity
    # sum over planets product of abs pos and abs vel
    positions = tuple(zip(xs, ys, zs))
    velocities = tuple(zip(vxs, vys, vzs))
    return sum(
        sum(map(abs, positions[planet_idx])) * sum(map(abs, velocities[planet_idx]))
        for planet_idx in range(num_planets)
    )


def part_two(lines: Iterable[str]) -> int:
    positions = parse(lines)
    num_planets = len(positions)

    # Break into the axes, operate on them independently
    xs, ys, zs = list(map(list, zip(*positions)))
    vxs, vys, vzs = [0] * num_planets, [0] * num_planets, [0] * num_planets

    # Find cycles for each axis independently
    # Answer is LCM of cycle lens
    x_cycle = find_cycle(xs, vxs)
    y_cycle = find_cycle(ys, vys)
    z_cycle = find_cycle(zs, vzs)
    return math.lcm(x_cycle, y_cycle, z_cycle)
