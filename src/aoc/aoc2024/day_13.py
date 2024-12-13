#!/usr/bin/env python
"""
PART 1
Claw machine with two buttons A and B.
A costs 3 tokens to press, B costs 1.
A and B both move the claw some amount along x and y.
Find out how to reach a target X and Y by pressing A and B (if possible)
with the minimum number of tokens (i.e. min A presses).
Limit A and B presses to <= 100 (though I don't think that is necessary...)

Notes
2D matrix eqn
M = {{Ax, Bx},{Ay, By}}*{x, y} = {X, Y}

To invert this matrix first we find the determinant
d = Ax*By - Bx*Ay
which I have to guess might be 0.
If d≠0, inverse is
M^-1 = 1/d {{By, -Bx},{-Ay, Ax}}
and answer is
{x, y} = M^-1 * {X, Y}

PART 2
Add 10000000000000 to all the target X and Y values.
Do not limit A and B presses to <= 100.
"""
import itertools
import logging
import re
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
"""
PART_ONE_EXAMPLE_RESULT = 480
PART_ONE_RESULT = 32026
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 89013607072065

log = logging.getLogger(__name__)


type Vec2 = tuple[int, int]
type OpVec2 = Vec2 | tuple[None, None]

BUTTON_RE = re.compile(r"Button (?P<button>[AB]): X\+(?P<X>\d+), Y\+(?P<Y>\d+)")
TARGET_RE = re.compile(r"Prize: X=(?P<X>\d+), Y=(?P<Y>\d+)")


def solve(a: Vec2, b: Vec2, target: Vec2, part2: bool = False) -> OpVec2:
    ax, ay = a
    bx, by = b
    tx, ty = target

    if part2:
        tx += 10000000000000
        ty += 10000000000000

    # Can we invert the matrix?
    det = ax * by - ay * bx
    if det == 0:
        return None, None

    # Invert the (A, B) matrix
    x = (tx * by - ty * bx) / det
    y = (-tx * ay + ty * ax) / det

    # Are solutions integers?
    if not (x % 1 == 0 and y % 1 == 0):
        return None, None
    x, y = int(x), int(y)

    if not part2:
        # Are solutions within bounds
        if not (0 <= x <= 100 and 0 <= y <= 100):
            return None, None

    return x, y


def parse(lines: Iterable[str]) -> list[tuple[Vec2, Vec2, Vec2]]:
    inputs: list[tuple[Vec2, Vec2, Vec2]] = []
    for group in itertools.batched(lines, 4):
        log.debug("group %s", group)
        a, b, target = None, None, None
        if (m := BUTTON_RE.match(group[0])) is not None:
            a = int(m.group("X")), int(m.group("Y"))
        if (m := BUTTON_RE.match(group[1])) is not None:
            b = int(m.group("X")), int(m.group("Y"))
        if (m := TARGET_RE.match(group[2])) is not None:
            target = int(m.group("X")), int(m.group("Y"))
        if any(x is None for x in (a, b, target)):
            log.debug("a %s", a)
            log.debug("b %s", b)
            log.debug("target %s", target)
            raise ValueError("Parsing problem")
        inputs.append((a, b, target))
    return inputs


def part_one(lines: Iterable[str]) -> int:
    inputs = parse(lines)
    solutions = [solve(*_input) for _input in inputs]
    return sum(3 * x + y for x, y in solutions if x is not None and y is not None)


def part_two(lines: Iterable[str]) -> int:
    inputs = parse(lines)
    solutions = [solve(*_input, part2=True) for _input in inputs]
    return sum(3 * x + y for x, y in solutions if x is not None and y is not None)
