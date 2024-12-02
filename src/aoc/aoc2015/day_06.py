#!/usr/bin/env python
"""
PART 1
Receive instructions to turn on, turn off, or toggle lights of certain ranges
of a 2D coordinate grid.
Count how many lights are on.

PART 2
Now "turn on" means + 1, "turn off" means - 1, and "toggle" means + 2
Start brightness at 0, do not let it drop below 0.
Find total brightness.
"""
import itertools
import logging
import math
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, NamedTuple, Self

PART_ONE_EXAMPLE = """\
turn on 0,0 through 999,999
toggle 0,0 through 999,0
turn off 499,499 through 500,500
"""
PART_ONE_EXAMPLE_RESULT = 1000 * 1000 - 1000 - 4
PART_ONE_RESULT = 377891
PART_TWO_EXAMPLE = """\
turn on 0,0 through 0,0
toggle 0,0 through 999,999
"""
PART_TWO_EXAMPLE_RESULT = 2000001
PART_TWO_RESULT = 14110788


RANGE_MIN = 0
RANGE_MAX = 999

LINE_RE = re.compile(
    r"(?P<instruction>[turnofgle ]+) "
    r"(?P<x0>\d+),(?P<y0>\d+) through (?P<x1>\d+),(?P<y1>\d+)"
)


log = logging.getLogger(__name__)


type Instruction = Literal["turn on", "turn off", "toggle"]


@dataclass(frozen=True, repr=False)
class Range:
    start: int
    end: int

    def is_empty(self) -> bool:
        return self.start > self.end

    def overlaps(self: Self, other: Self) -> bool:
        return (
            not other.is_empty()
            and not self.is_empty()
            and self.start <= other.end
            and other.start <= self.end
        )

    def __and__(self: Self, other: Self) -> Self:
        """Overlap between self and other"""
        if not self.overlaps(other):
            return EmptyRange
        lower = max(self.start, other.start)
        upper = min(self.end, other.end)
        return Range(lower, upper)

    def __sub__(self: Self, other: Self) -> list[Self]:
        """Non-overlapping parts of self and other
        (lower and upper). Either or both may be EmptyRange."""
        # Non-overlapping cases
        if other.end < self.start or self.end < other.start:
            # Self is above or below
            return [self]

        # Some overlap exists
        shards = []
        if self.start < other.start:
            shards.append(Range(self.start, other.start - 1))
        if self.end > other.end:
            shards.append(Range(other.end + 1, self.end))

        return shards

    def __len__(self) -> int:
        return self.end - self.start + 1

    def __repr__(self):
        return f"{self.start},{self.end}"


EmptyRange = Range(0, -1)
FullRange = Range(RANGE_MIN, RANGE_MAX)


@dataclass(frozen=True, repr=False)
class Area:
    x: Range = FullRange
    y: Range = FullRange

    @staticmethod
    def from_points(
        x0: str | int, y0: str | int, x1: str | int, y1: str | int
    ) -> "Self":
        return Area(Range(int(x0), int(x1)), Range(int(y0), int(y1)))

    @property
    def dimensions(self) -> tuple[Range, Range]:
        return self.x, self.y

    def __iter__(self):
        yield self.x
        yield self.y

    def __and__(self: Self, other: Self) -> Self:
        """Find overlapping area between self and other.
        Can be EmptyArea."""
        if other is EmptyArea or self is EmptyArea:
            return EmptyArea
        # if other is FullArea:
        #     return self
        # if self is FullArea:
        #     return other
        dimensions = []
        for self_dimension, other_dimension in zip(self, other):
            and_dimension = self_dimension & other_dimension
            if and_dimension is EmptyRange:
                return EmptyArea
            dimensions.append(and_dimension)
        return Area(*dimensions)

    def __sub__(self: Self, other: Self) -> list[Self]:
        """Subtract other from self.
        (This is typically used with an "other" that is completely
        within self, but doesn't have to be I guess.)
        """
        overlap = self & other
        if overlap.is_empty():
            return [self]
        shards = []
        for x_shard in self.x - overlap.x:
            shards.append(Area(x_shard, self.y))

        for y_shard in self.y - overlap.y:
            shards.append(Area(overlap.x, y_shard))

        return shards

    def is_empty(self) -> bool:
        return any(dim.is_empty() for dim in self.dimensions)

    def __len__(self):
        return math.prod(map(len, self.dimensions))

    def __repr__(self):
        return f"{self.x};{self.y}"


EmptyArea = Area(EmptyRange, EmptyRange)
FullArea = Area(FullRange, FullRange)


@dataclass(frozen=True, repr=False)
class Lights:
    area: Area
    brightness: int
    is_part_one: bool

    def adjust_brightness(self, amount: int, area: Area) -> list[Self]:
        """Turn on any overlap between self and area"""
        if self.is_part_one and (
            self.brightness == amount == 1 or self.brightness == 0 and amount == -1
        ):
            # Already set to on/off. Nothing to do.
            return [self]
        overlap = self.area & area
        if overlap.is_empty():
            # No overlap. Nothing to do.
            return [self]
        light_shards = [
            Lights(shard, self.brightness, self.is_part_one)
            for shard in self.area - overlap
        ]
        return [
            *light_shards,
            Lights(overlap, max(self.brightness + amount, 0), self.is_part_one),
        ]

    def turn_on(self, area: Area) -> list[Self]:
        """Turn on any overlap between self and area"""
        return self.adjust_brightness(1, area)

    def turn_off(self, area: Area) -> list[Self]:
        """Turn off any overlap between self and area"""
        return self.adjust_brightness(-1, area)

    def toggle(self, area: Area) -> list[Self]:
        """Find overlap of self and other. Flip that to other state.
        Keep all other shards the same."""
        adjustment = 2 if not self.is_part_one else -1 if self.brightness == 1 else 1
        return self.adjust_brightness(adjustment, area)

    def __len__(self: Self) -> int:
        if self.is_part_one:
            return len(self.area) if self.brightness == 1 else 0
        return len(self.area) * self.brightness

    def __repr__(self):
        return f"Lights({self.brightness}, {self.area})"


class Line(NamedTuple):
    instruction: Instruction
    area: Area


def parse_line(line: str) -> Line:
    if m := LINE_RE.match(line):
        instruction = m.group("instruction")
        area = Area.from_points(
            m.group("x0"), m.group("y0"), m.group("x1"), m.group("y1")
        )
        return Line(instruction, area)
    raise RuntimeError("Could not parse line " + line)


def find_brightness(lines: Iterable[str], is_part_one: bool) -> int:
    lights = [Lights(FullArea, 0, is_part_one)]
    for line in lines:
        if log.isEnabledFor(logging.DEBUG):
            log.debug("lights: %s", lights)
        instruction, area = parse_line(line)
        if instruction == "turn on":
            operation = Lights.turn_on
        elif instruction == "turn off":
            operation = Lights.turn_off
        else:
            operation = Lights.toggle
        lights = list(
            itertools.chain.from_iterable(operation(light, area) for light in lights)
        )
    return sum(len(light) for light in lights)


def part_one(lines: Iterable[str]) -> int:
    return find_brightness(lines, True)


def part_two(lines: Iterable[str]) -> int:
    return find_brightness(lines, False)
