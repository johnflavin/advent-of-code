#!/usr/bin/env python
"""
PART 1
Given a list of sensor positions and the positions of their
closest beacons, count locations where the beacons cannot be located on
a target row (row 10 for example, row 2000000 for real input).

PART 2
"""
import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass

from aoc.util import Coord, Range, EmptyRange


PART_ONE_EXAMPLE = """\
Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3
"""
PART_ONE_EXAMPLE_RESULT = 26
PART_ONE_RESULT = 4951427
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 56000011
PART_TWO_RESULT = 13029714573243

PART_ONE_EXAMPLE_ROW = 10
PART_ONE_ROW = 2000000
PART_TWO_EXAMPLE_AREA_LEN = 21
PART_TWO_AREA_LEN = 4000001


log = logging.getLogger(__name__)


SENSOR_INPUT_RE = re.compile(
    r"Sensor at x=(?P<sx>-?\d+), y=(?P<sy>-?\d+): "
    + r"closest beacon is at x=(?P<bx>-?\d+), y=(?P<by>-?\d+)"
)


@dataclass
class Sensor:
    pos: Coord
    nearest_beacon: Coord

    def __post_init__(self):
        px, py = self.pos
        bx, by = self.nearest_beacon
        self.beacon_distance = abs(px - bx) + abs(py - by)

    def excluded_range(self, row: int) -> Range:
        px, py = self.pos
        # How far is the target row vertically from the pos?
        y_distance = abs(row - py)
        # How much distance is left over?
        x_distance = self.beacon_distance - y_distance
        log.debug(self)
        log.debug("  dist_beacon=%d dist_row=%d", self.beacon_distance, y_distance)
        log.debug("  dist_beacon - dist_row=%d", x_distance)
        if x_distance >= 0:
            r = Range(px - x_distance, px + x_distance)
            log.debug(" range=%s", r)
            return r
        else:
            log.debug(" empty range")
            return EmptyRange


def determine_target_row(sensors: list[Sensor]) -> int:
    """Should we use the target row from the example, or the real thing?"""
    not_example = any(s.pos[0] > 100 or s.pos[1] > 100 for s in sensors)
    return PART_ONE_ROW if not_example else PART_ONE_EXAMPLE_ROW


def determine_target_area(sensors: list[Sensor]) -> int:
    """Should we use the target row from the example, or the real thing?"""
    not_example = any(s.pos[0] > 100 or s.pos[1] > 100 for s in sensors)
    return PART_TWO_AREA_LEN if not_example else PART_TWO_EXAMPLE_AREA_LEN


def make_disjoint(r: Range, known_disjoint: Iterable[Range]) -> Iterable[Range]:
    """Remove overlaps between a range and a list of others by sharding others"""
    for k in known_disjoint:
        for shard in k - r:
            if shard is EmptyRange:
                continue
            yield shard


def make_all_disjoint(ranges: Iterable[Range]) -> list[Range]:
    """Break ranges into non-overlapping shards"""
    known_disjoint = []
    for stable in ranges:
        known_disjoint = list(make_disjoint(stable, known_disjoint))
        known_disjoint.append(stable)
    return known_disjoint


def find_excluded_ranges(sensors: list[Sensor], target_row: int) -> list[Range]:
    excluded_ranges = [
        ex for s in sensors if (ex := s.excluded_range(target_row)) is not EmptyRange
    ]
    log.debug("excluded ranges on row %d: %s", target_row, excluded_ranges)
    disjoint_excluded_ranges = make_all_disjoint(excluded_ranges)
    log.debug(
        "disjoint excluded ranges on row %d: %s",
        target_row,
        disjoint_excluded_ranges,
    )
    return disjoint_excluded_ranges


def part_one(lines: Iterable[str]) -> int:
    sensors = [
        Sensor(
            (int(m.group("sx")), int(m.group("sy"))),
            (int(m.group("bx")), int(m.group("by"))),
        )
        for line in lines
        if (m := SENSOR_INPUT_RE.match(line)) is not None
    ]
    beacons = set(s.nearest_beacon for s in sensors)

    target_row = determine_target_row(sensors)

    excluded_ranges = find_excluded_ranges(sensors, target_row)
    range_len = sum(len(r) for r in excluded_ranges)
    return range_len - sum(
        1
        for bx, by in beacons
        if by == target_row and any(bx in r for r in excluded_ranges)
    )


def part_two(lines: Iterable[str]) -> int:
    sensors = [
        Sensor(
            (int(m.group("sx")), int(m.group("sy"))),
            (int(m.group("bx")), int(m.group("by"))),
        )
        for line in lines
        if (m := SENSOR_INPUT_RE.match(line)) is not None
    ]
    beacons = set(s.nearest_beacon for s in sensors)
    square_len = determine_target_area(sensors)

    def combine_ranges(disjoint_ranges: list[Range]) -> Iterable[Range]:
        sorted_ranges = sorted(disjoint_ranges, reverse=True)
        if not sorted_ranges:
            return
        start_range = sorted_ranges.pop()
        current_low, current_up = start_range.lower, start_range.upper
        while sorted_ranges:
            a_range = sorted_ranges.pop()
            if current_up == a_range.lower + 1:
                # No gap, combine
                current_up = a_range.upper
            else:
                # Gap, emit what we have and start a new range
                yield Range(current_low, current_up)
                current_low = a_range.lower
                current_up = a_range.upper
        # No more ranges, emit what we have left
        yield Range(current_low, current_up)

    def find_gaps(ranges: Iterable[Range]) -> Iterable[int]:
        """Start with the full range. Successively subtract off
        ranges from the (sorted) list. Emit anything to the left,
        make the right the new range to subtract from.
        Once we're out of ranges to subtract, emit everything to the right."""
        right = Range(0, square_len)
        for r in ranges:
            sub = right - r
            if len(sub) == 2:
                left, right = tuple(sub)
            elif not sub:
                # Nothing left
                left = EmptyRange
                right = EmptyRange
            elif sub[0] < r:
                left = sub[0]
                right = EmptyRange
            elif sub[0] > r:
                left = EmptyRange
                right = sub[0]
            else:
                raise RuntimeError(f"Don't know what to do with {right=} {r=} {sub=}")
            yield from left
        yield from right

    for row, target_row in enumerate(range(square_len)):
        if row % 50000 == 0 and log.isEnabledFor(logging.DEBUG):
            log.debug("Row %d", row)
        excluded_ranges = find_excluded_ranges(sensors, target_row)
        range_len = sum(len(r) for r in excluded_ranges)
        if range_len == square_len:
            continue
        log.debug("Row %d has at least one gap", row)
        combined = combine_ranges(excluded_ranges)
        for gap_x in find_gaps(combined):
            if (gap_x, row) in beacons:
                log.debug("Gap (%d, %d) is a beacon")
                continue
            else:
                log.debug("Found a real gap at (%d, %d)", gap_x, row)
                return gap_x * 4000000 + row

    return -1
