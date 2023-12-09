#!/usr/bin/env python
"""

PART 1
List contains seeds to be planted, then maps from one category to another.

Each X-to-Y map lists three numbers per line:
destination range start, source range start, range length
Any numbers that are in those ranges are mapped to each other, one-to-one.
Any other numbers not in a range map to the same numbers.

Starting from the initial seeds, following the mapped numbers, what is
the lowest location number?

PART 2
Now the initial seed numbers are not four numbers, they are
two ranges in the form of (range start, range len).
Find the lowest location for any number in those seed ranges.

I tried implementing this the naive way, using literal ranges of numbers
and checking them all.
Doesn't seem like it will finish within a reasonable time.
Need to think this through.

We need a way to compose two maps into a new map.
Then we can compress all the maps down into a single map.
And that includes the initial seed ranges, which are their own map.
Composing maps will mean taking two sets of ranges, the
A-to-B and a B-to-C, and turning that into a set of
A-to-C ranges.

How can we do that?

Union all the ranges together.
Order them by the intermediate layer.
Where there are non-overlapping ranges, they just come in as-is. The other side is
    the identity in that section.
Where there are overlapping sections, take the start and end from the
    outer source and dest, the ones that aren't being removed.
Where there are semi-overlapping ranges, cut them up into strictly non-overlapping
    and strictly overlapping ranges.
Once we compose all the ranges, we will have a full start-to-finish map.

To answer the question, we turn the seed ranges into another map.
This one is identity everywhere. But making it will allow us to apply our
    overlap techniques to find where the seed ranges map to.
We do the same thing where we cut up the overlapping and non-overlapping parts.
Except this time we throw the non-overlapping parts away.
This is an intersection, not a union.
One we intersect the seed ranges with the map, the lowest location
destination range start is the answer.
"""
import itertools
import re
from collections.abc import Iterable
from dataclasses import dataclass, field


PART_ONE_EXAMPLE = """\
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
"""
PART_ONE_EXAMPLE_RESULT = 35
PART_ONE_RESULT = 51752125
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 46
PART_TWO_RESULT = 12634632


title_re = re.compile("^(?P<source>[a-z]+)-to-(?P<dest>[a-z]+) map:$")


@dataclass
class MapRange:
    source_start: int
    dest_start: int
    range_len: int

    def __init__(
        self, dest_start: str | int, source_start: str | int, range_len: str | int
    ):
        self.source_start = int(source_start)
        self.dest_start = int(dest_start)
        self.range_len = int(range_len)

    @property
    def source_end(self) -> int:
        return self.source_start + self.range_len

    @property
    def dest_end(self) -> int:
        return self.dest_start + self.range_len

    @property
    def delta(self):
        return self.dest_start - self.source_start

    def shift(self, delta: int):
        self.source_start += delta
        self.dest_start += delta
        self.range_len -= delta


def union_ranges(
    dest_ranges: list[MapRange], source_ranges: list[MapRange]
) -> list[MapRange]:
    combined = []
    while dest_ranges or source_ranges:
        # If one or the other is empty we can be done
        if not dest_ranges:
            combined.extend(source_ranges)
            break
        if not source_ranges:
            combined.extend(dest_ranges)
            break

        # Ok, neither is empty
        source = source_ranges.pop()
        dest = dest_ranges.pop()

        # Check cases of no overlap
        if source.source_end < dest.dest_start:
            combined.append(source)
            dest_ranges.append(dest)
            continue
        if dest.dest_end < source.source_start:
            combined.append(dest)
            source_ranges.append(source)
            continue

        # The ranges overlap. We will need to break them apart
        if source.source_start < dest.dest_start:
            # Find length of new range
            length = dest.dest_start - source.source_start

            # Create new non-overlapping range
            combined.append(MapRange(source.dest_start, source.source_start, length))

            # Put back one that isn't changing
            dest_ranges.append(dest)

            # Shorten other range and put it back too
            source.shift(length)
            source_ranges.append(source)
        elif source.source_start > dest.dest_start:
            # Find length of new range
            length = source.source_start - dest.dest_start

            # Create new non-overlapping range
            combined.append(MapRange(dest.dest_start, dest.source_start, length))

            # Put back one that isn't changing
            source_ranges.append(source)

            # Shorten other range and put it back too
            dest.shift(length)
            dest_ranges.append(dest)
        elif source.source_end < dest.dest_end:
            # Create new overlapping range
            combined.append(
                MapRange(source.dest_start, dest.source_start, source.range_len)
            )

            # We can drop the source range now
            # Shorten dest range and put it back
            dest.shift(source.range_len)
            dest_ranges.append(dest)
        elif source.source_end > dest.dest_end:
            # Create new overlapping range
            combined.append(
                MapRange(source.dest_start, dest.source_start, dest.range_len)
            )

            # We can drop the dest range now
            # Shorten source range and put it back
            source.shift(dest.range_len)
            source_ranges.append(source)
        else:
            # Ranges are exactly equal.
            # Make a combined range that covers both.
            combined.append(
                MapRange(source.dest_start, dest.source_start, dest.range_len)
            )

    return combined


def intersect_ranges(
    dest_ranges: list[MapRange], source_ranges: list[MapRange]
) -> list[MapRange]:
    combined = []
    while dest_ranges and source_ranges:
        source = source_ranges.pop()
        dest = dest_ranges.pop()

        # Check cases of no overlap
        if source.source_end < dest.dest_start:
            # Skip source
            dest_ranges.append(dest)
            continue
        if dest.dest_end < source.source_start:
            # Skip dest
            source_ranges.append(source)
            continue

        # The ranges overlap. We will need to break them apart
        if source.source_start < dest.dest_start:
            # Find overlapping length
            length = dest.dest_start - source.source_start

            # Put back one that isn't changing
            dest_ranges.append(dest)

            # Shorten other range and put it back too
            source.shift(length)
            source_ranges.append(source)
        elif source.source_start > dest.dest_start:
            # Find overlapping length
            length = source.source_start - dest.dest_start

            # Put back one that isn't changing
            source_ranges.append(source)

            # Shorten other range and put it back too
            dest.shift(length)
            dest_ranges.append(dest)
        elif source.source_end < dest.dest_end:
            # Create new overlapping range
            combined.append(
                MapRange(source.dest_start, dest.source_start, source.range_len)
            )

            # We can drop the source range now
            # Shorten dest range and put it back
            dest.shift(source.range_len)
            dest_ranges.append(dest)
        elif source.source_end > dest.dest_end:
            # Create new overlapping range
            combined.append(
                MapRange(source.dest_start, dest.source_start, dest.range_len)
            )

            # We can drop the dest range now
            # Shorten source range and put it back
            source.shift(dest.range_len)
            source_ranges.append(source)
        else:
            # Ranges are exactly equal.
            # Make a combined range that covers both.
            combined.append(
                MapRange(source.dest_start, dest.source_start, dest.range_len)
            )

    return combined


@dataclass
class Map:
    source: str
    dest: str
    ranges: list[MapRange] = field(default_factory=list)

    def map(self, source_num: int) -> int:
        for _range in self.ranges:
            if _range.source_start <= source_num <= _range.source_end:
                return source_num + _range.delta
        return source_num

    def union(self, other: "Map"):
        # Match this map's dest with the other map's source
        assert self.dest == other.source
        self.ranges.sort(key=lambda rang: rang.dest_start, reverse=True)
        other.ranges.sort(key=lambda rang: rang.source_start, reverse=True)

        self.ranges = union_ranges(self.ranges, other.ranges)
        self.dest = other.dest

    def intersect(self, other: "Map"):
        # Match this map's dest with the other map's source
        assert self.dest == other.source
        self.ranges.sort(key=lambda rang: rang.dest_start, reverse=True)
        other.ranges.sort(key=lambda rang: rang.source_start, reverse=True)

        self.ranges = intersect_ranges(self.ranges, other.ranges)
        self.dest = other.dest


def parse_lines(lines: Iterable[str]) -> tuple[list[int], Map]:
    lines = iter(lines)

    # Read seeds
    seed_line = next(lines)
    _, seed_num_strs = seed_line.split(": ")
    seed_nums = [int(seed_num) for seed_num in seed_num_strs.split()]

    # Blank
    next(lines)

    # Parse maps
    the_map = None
    while True:
        try:
            title = next(lines)
        except StopIteration:
            break
        if not title:
            break
        # Parse title, make a Map
        if title_match := title_re.match(title):
            source = title_match.group("source")
            dest = title_match.group("dest")
        else:
            raise Exception(f"Could not parse title {title}")
        a_map = Map(source, dest)

        # Read range strs, make Ranges
        while True:
            try:
                range_str = next(lines)
            except StopIteration:
                break
            if not range_str:
                break
            a_map.ranges.append(MapRange(*range_str.split()))

        if the_map is None:
            the_map = a_map
        else:
            the_map.union(a_map)

    return seed_nums, the_map


def part_one(lines: Iterable[str]) -> int:
    nums, the_map = parse_lines(lines)
    nums = [the_map.map(num) for num in nums]
    return min(nums)


def part_two(lines: Iterable[str]) -> int:
    """
    Union all the maps as before, but now make all the seed ranges into a map too.
    And then intersect that one with the transformation map.
    Simply read off the lowest location.
    """
    nums, the_map = parse_lines(lines)
    assert len(nums) % 2 == 0
    nums_map = Map("seed", "seed")
    nums_map.ranges = [
        MapRange(rstart, rstart, rlen) for rstart, rlen in itertools.batched(nums, 2)
    ]

    nums_map.intersect(the_map)
    return min(a_range.dest_start for a_range in nums_map.ranges)
