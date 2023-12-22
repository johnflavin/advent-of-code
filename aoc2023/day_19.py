#!/usr/bin/env python
"""

PART 1
Given a list of workflows and a list of ratings.
Ratings have four ints: x, m, a, and s
Workflows are made of rules. Based on one of the values of a rating,
    it can be accepted, rejected, or send to another workflow.
Run the workflows on all ratings, staring with workflow "in".
Sum the x, m, a, and s values of all accepted ratings.

PART 2
Ignore the ratings in the input.
Ratings' attributes can all range from 1 to 4000.
Sum the x, m, a, and s values of all possible ratings that would be accepted.
"""

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from functools import cache
from itertools import product
from math import prod
from typing import Self


PART_ONE_EXAMPLE = """\
px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

{x=787,m=2655,a=1222,s=2876}
{x=1679,m=44,a=2067,s=496}
{x=2036,m=264,a=79,s=2244}
{x=2461,m=1339,a=466,s=291}
{x=2127,m=1623,a=2188,s=1013}
"""
PART_ONE_EXAMPLE_RESULT = 19114
PART_ONE_RESULT = 421983
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 167409079868000
PART_TWO_RESULT = None


RATING_RE = re.compile(r"{x=(?P<x>\d+),m=(?P<m>\d+),a=(?P<a>\d+),s=(?P<s>\d+)}")
CONDITION_RE = re.compile(r"(?P<attribute>[xmas])(?P<comparator>[<>])(?P<value>\d+)")


RANGE_MIN = 1
RANGE_MAX = 4000

log = logging.getLogger(__name__)


class Dimension(Enum):
    x = 0
    m = 1
    a = 2
    s = 3


type Rating = dict[Dimension, int]
type Result = bool | str


@dataclass
class Range:
    lower: int
    upper: int

    def overlaps(self: Self, other: Self) -> bool:
        return self.lower <= other.upper + 1 and other.lower <= self.upper + 1

    def __and__(self: Self, other: Self | "OrRange") -> Self | "OrRange":
        if isinstance(other, OrRange):
            return other & self
        if self.overlaps(other):
            lower = max(self.lower, other.lower)
            upper = min(self.upper, other.upper)
            return Range(lower, upper)
        return EmptyRange

    def __or__(self: Self, other: Self | "OrRange") -> Self | "OrRange":
        if isinstance(other, OrRange):
            return other | self

        if self is EmptyRange:
            return other
        if other is EmptyRange:
            return self

        if self.overlaps(other):
            lower = min(self.lower, other.lower)
            upper = max(self.upper, other.upper)
            return Range(lower, upper)

        return OrRange((self, other))

    def __contains__(self, item: int) -> bool:
        return self.lower <= item <= self.upper

    def partition(self: Self, value: int, gt: True) -> tuple[Self, Self]:
        if gt and value >= self.upper or not gt and value <= self.lower:
            return EmptyRange, self
        elif gt and value < self.lower or not gt and value > self.upper:
            return EmptyRange, self
        elif gt:
            return Range(value + 1, self.upper), Range(self.lower, value)
        else:
            return Range(self.lower, value - 1), Range(value, self.upper)

    @property
    def size(self):
        return self.upper - self.lower + 1


EmptyRange = Range(-2, -2)
FullRange = Range(RANGE_MIN, RANGE_MAX)


@dataclass
class OrRange:
    ranges: tuple[Range, ...]

    def __post_init__(self):
        self.ranges = tuple(
            _range for _range in self.ranges if _range is not EmptyRange
        )

    def __and__(self: Self, other: Self | Range) -> Self | Range:
        if isinstance(other, OrRange):
            other_ranges = other.ranges
        elif isinstance(other, Range):
            if other is EmptyRange:
                return EmptyRange
            if other is FullRange:
                return self

            other_ranges = [other]
        else:
            raise RuntimeError(f"Cannot and OrRange and {type(other)}")
        return OrRange(
            *tuple(
                range_a & range_b
                for range_a, range_b in product(self.ranges, other_ranges)
            )
        )

    def __or__(self: Self, other: Self | Range) -> Self | Range:
        if isinstance(other, OrRange):
            possibly_overlapping_ranges = list(other.ranges)
        elif isinstance(other, Range):
            if other is EmptyRange:
                return self
            if other is FullRange:
                return FullRange

            possibly_overlapping_ranges = [other]
        else:
            raise RuntimeError(f"Cannot or OrRange and {type(other)}")

        known_nonoverlapping_ranges = list(self.ranges)
        while possibly_overlapping_ranges:
            range_a = possibly_overlapping_ranges.pop()
            for b_idx, range_b in enumerate(list(known_nonoverlapping_ranges)):
                or_ab = range_a | range_b
                if isinstance(or_ab, Range):
                    # We know neither is empty. So a Range means they overlapped.
                    known_nonoverlapping_ranges.pop(b_idx)
                    possibly_overlapping_ranges.append(or_ab)
                    break
            else:
                # No overlaps with anything. We can keep it.
                known_nonoverlapping_ranges.append(range_a)

        return (
            OrRange(tuple(known_nonoverlapping_ranges))
            if len(known_nonoverlapping_ranges) > 1
            else known_nonoverlapping_ranges[0]
        )

    def __contains__(self, item):
        return any(item in _range for _range in self.ranges)

    def __iter__(self):
        return iter(self.ranges)

    def partition(self, value: int, gt: bool) -> tuple[Self | Range, Self | Range]:
        trues, falses = zip(_range.partition(value, gt) for _range in self.ranges)
        return (
            OrRange(trues)
            if not all(_range is EmptyRange for _range in trues)
            else EmptyRange,
            OrRange(falses)
            if not all(_range is EmptyRange for _range in falses)
            else EmptyRange,
        )

    @property
    def size(self):
        return sum(_range.size for _range in self.ranges)


@dataclass
class Volume:
    dimensions: tuple[Range | OrRange, ...] = field(
        default_factory=lambda: tuple(FullRange for _ in range(4))
    )

    def __and__(self: Self, other: Self | "OrVolume") -> Self | "OrVolume":
        if isinstance(other, OrVolume):
            return other & self
        if other is EmptyVolume or self is EmptyVolume:
            return EmptyVolume
        if other is FullVolume:
            return self
        if self is FullVolume:
            return other
        dimensions = []
        for self_dimension, other_dimension in zip(self.dimensions, other.dimensions):
            and_dimension = self_dimension & other_dimension
            if and_dimension is EmptyRange:
                return EmptyVolume
            dimensions.append(and_dimension)
        return Volume(tuple(dimensions))

    def __or__(self: Self, other: Self) -> Self | "OrVolume":
        if other is EmptyVolume:
            return self
        if self is EmptyVolume:
            return other
        if other is FullVolume or self is FullVolume:
            return FullVolume
        dimensions = []
        for self_dimension, other_dimension in zip(self.dimensions, other.dimensions):
            dimension = self_dimension | other_dimension
            if isinstance(dimension, Range):
                dimension = OrRange(dimension)
            dimensions.append(dimension)
        return OrVolume(
            tuple(
                Volume(dims)
                if not any(_dim == EmptyRange for _dim in dims)
                else EmptyVolume
                for dims in product(*dimensions)
            )
        )

    def __contains__(self, item: Rating):
        return all(value in self.dimensions[dim.value] for dim, value in item.items())

    def partition(
        self, dimension: Dimension, value: int, gt: bool
    ) -> tuple[Self, Self]:
        true_dims, false_dims = list(self.dimensions), list(self.dimensions)
        true_dims[dimension.value], false_dims[dimension.value] = self.dimensions[
            dimension.value
        ].partition(value, gt)

        return (
            (
                Volume(tuple(true_dims))
                if true_dims[dimension.value] is not EmptyRange
                else EmptyVolume
            ),
            (
                Volume(tuple(false_dims))
                if false_dims[dimension.value] is not EmptyRange
                else EmptyVolume
            ),
        )

    @property
    def size(self):
        return prod(dim.size for dim in self.dimensions)


EmptyVolume = Volume(tuple(EmptyRange for _ in range(4)))
FullVolume = Volume()


@dataclass
class OrVolume:
    volumes = tuple[Volume, ...]

    def __post_init__(self):
        self.volumes = (vol for vol in self.volumes if vol is not EmptyVolume)


@cache
def is_debug() -> bool:
    return log.isEnabledFor(logging.DEBUG)


@cache
def parse_rule_result_str(result: str) -> Result:
    if result == "A":
        return True
    elif result == "R":
        return False
    else:
        return result


def parse_rating_line(line: str) -> Rating:
    if match := RATING_RE.match(line):
        return {Dimension[k]: int(v) for k, v in match.groupdict().items()}


def parse_rules(rules_str: str) -> dict[Result, Volume]:
    log.debug(f" + Parsing rules {rules_str}")

    rules: dict[Result, Volume] = {}
    volume_buffer = FullVolume
    for rule_str in rules_str.split(","):
        condition_and_result = rule_str.split(":")
        if len(condition_and_result) == 1:
            # Whatever is left over in the unknown range leads to this result
            result = parse_rule_result_str(condition_and_result[0])

            if result in rules:
                rules[result] |= volume_buffer
            else:
                rules[result] = volume_buffer
        else:
            # Partition the unknown range based on the condition
            # When the condition is met, we know the result.
            # When the condition is not met, we do not yet know the result.
            condition, result_str = condition_and_result
            result = parse_rule_result_str(result_str)

            if match := CONDITION_RE.match(condition):
                attribute = match.group("attribute")
                dimension = Dimension[attribute]
                value = int(match.group("value"))

                gt = match.group("comparator") == ">"

                # Whatever partition we have now is ANDed with all the ones before
                # We now know the result for another part of the range
                true_vol, false_vol = volume_buffer.partition(dimension, value, gt)
                if result in rules:
                    rules[result] |= true_vol
                else:
                    rules[result] = true_vol

                # Add the inverse of this partition to the buffer for the next rule
                volume_buffer = false_vol
            else:
                raise RuntimeError("Could not parse rule " + rule_str)

    log.debug(" ++ Parsed rules")
    for result, volumes in rules.items():
        log.debug(f" ++++ {result}: {volumes}")

    return rules


def consolidate(workflows: dict[str, dict[Result, Volume]]) -> Volume:
    true_volume = workflows["in"].get(True, EmptyVolume)
    workflows_to_pull = {
        key: volume for key, volume in workflows["in"].items() if isinstance(key, str)
    }

    while workflows_to_pull:
        # if True in ranges_by_result:
        #     accepted = consolidate_ranges(accepted, ranges_by_result.pop(True))
        # if False in ranges_by_result:
        #     _ = ranges_by_result.pop(False)

        starting_workflow_name, starting_volume = workflows_to_pull.popitem()

        for other_result_or_workflow_name, other_volume in workflows[
            starting_workflow_name
        ].items():
            if other_result_or_workflow_name is False:
                # We don't care about False
                continue
            combined_volume = starting_volume & other_volume

            if other_result_or_workflow_name is True:
                true_volume |= combined_volume
            elif isinstance(other_result_or_workflow_name, str):
                # This result points to another workflow
                # Store it to pull up later
                if other_result_or_workflow_name in workflows_to_pull:
                    workflows_to_pull[other_result_or_workflow_name] |= combined_volume
                else:
                    workflows_to_pull[other_result_or_workflow_name] = combined_volume

    return true_volume


def parse(lines: Iterable[str]) -> tuple[Volume, tuple[Rating, ...]]:
    lines = iter(lines)

    # Parse workflows
    workflow_tuples = []
    while line := next(lines):
        workflow_tuples.append(parse_rule_line(line))
    workflows = dict(workflow_tuples)

    # Parse ratings
    ratings = tuple(map(parse_rating_line, lines))

    return consolidate(workflows), ratings


def parse_rule_line(line: str) -> tuple[str, dict[Result, Volume]]:
    name, rules_str = line[:-1].split("{")
    return name, parse_rules(rules_str)


def part_one(lines: Iterable[str]) -> int:
    true_volume, ratings = parse(lines)
    print("true:", true_volume)
    return sum(
        value
        for rating in ratings
        for value in rating.values()
        if rating in true_volume
    )


def part_two(lines: Iterable[str]) -> int:
    true_volume, _ = parse(lines)
    return true_volume.size
