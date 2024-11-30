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
from dataclasses import dataclass
from itertools import product
from math import prod
from typing import Literal, Self


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
PART_TWO_RESULT = 129249871135292


RATING_RE = re.compile(r"{x=(?P<x>\d+),m=(?P<m>\d+),a=(?P<a>\d+),s=(?P<s>\d+)}")
CONDITION_RE = re.compile(r"(?P<attribute>[xmas])(?P<comparator>[<>])(?P<value>\d+)")


RANGE_MIN = 1
RANGE_MAX = 4000

IN = "in"
ACCEPT = "A"
REJECT = "R"

Dim = Literal["x", "m", "a", "s"]

log = logging.getLogger(__name__)


type Rating = dict[Dim, int]
type Result = str


@dataclass(frozen=True, repr=False)
class Range:
    lower: int
    upper: int

    def __and__(self: Self, other: Self) -> Self:
        """Overlap between self and other"""
        if self.overlaps(other):
            lower = max(self.lower, other.lower)
            upper = min(self.upper, other.upper)
            return Range(lower, upper)
        return EmptyRange

    def __or__(self: Self, other: Self) -> Self:
        if self is EmptyRange:
            return other
        if other is EmptyRange:
            return self

    def __sub__(self: Self, other: Self) -> tuple[Self, Self]:
        """Non-overlapping parts of self and other
        (lower and upper). Either or both may be EmptyRange."""
        # Non-overlapping cases
        if other.upper < self.lower:
            # Self is above
            return EmptyRange, self
        elif self.upper < other.lower:
            # Self is below
            return self, EmptyRange

        # Some overlap exists
        if self.lower >= other.lower:
            lower_disjoint = EmptyRange
        else:
            lower_disjoint = Range(self.lower, other.lower - 1)
        if self.upper <= other.upper:
            upper_disjoint = EmptyRange
        else:
            upper_disjoint = Range(other.upper + 1, self.upper)

        return lower_disjoint, upper_disjoint

    def overlaps(self: Self, other: Self) -> bool:
        """Does this range overlap with another at all?

        >>> r = Range(2, 3)
        >>> r.overlaps(Range(3, 4))
        True
        >>> r.overlaps(Range(4, 5))
        False
        >>> r.overlaps(Range(1, 2))
        True
        >>> r.overlaps(Range(0, 1))
        False
        >>> r.overlaps(EmptyRange)
        False
        """
        return self.lower <= other.upper and other.lower <= self.upper

    def __contains__(self, item: int) -> bool:
        return self.lower <= item <= self.upper

    def partition(self: Self, value: int, gt: True) -> tuple[Self, Self]:
        """Partition this range into two: one where the condition is true
        and one where it is false"""
        if gt and value >= self.upper or not gt and value <= self.lower:
            return EmptyRange, self
        elif gt and value < self.lower or not gt and value > self.upper:
            return EmptyRange, self
        elif gt:
            return Range(value + 1, self.upper), Range(self.lower, value)
        else:
            return Range(self.lower, value - 1), Range(value, self.upper)

    def make_disjoint(self: Self, other: Self) -> tuple[Self, Self, Self]:
        """Split this range into three: the part that is strictly lower than
        the other, the part that overlaps the other, and the part that is
        strictly greater than the other."""

        overlap = self & other
        lower_disjoint, upper_disjoint = self - overlap
        return lower_disjoint, overlap, upper_disjoint

    @property
    def size(self):
        return self.upper - self.lower + 1

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"({self.lower}, {self.upper})"


EmptyRange = Range(-2, -2)
FullRange = Range(RANGE_MIN, RANGE_MAX)


@dataclass
class Volume:
    x: Range = FullRange
    m: Range = FullRange
    a: Range = FullRange
    s: Range = FullRange

    @property
    def dimensions(self) -> tuple[Range, Range, Range, Range]:
        return self.x, self.m, self.a, self.s

    @property
    def dim_dict(self) -> dict[Dim, Range]:
        return {
            "x": self.x,
            "m": self.m,
            "a": self.a,
            "s": self.s,
        }

    def __iter__(self):
        yield from self.dimensions

    def __and__(self: Self, other: Self) -> Self:
        if other is EmptyVolume or self is EmptyVolume:
            return EmptyVolume
        if other is FullVolume:
            return self
        if self is FullVolume:
            return other
        dimensions = []
        for self_dimension, other_dimension in zip(self, other):
            and_dimension = self_dimension & other_dimension
            if and_dimension is EmptyRange:
                return EmptyVolume
            dimensions.append(and_dimension)
        return Volume(*dimensions)

    def __or__(self: Self, other: Self) -> Iterable[Self]:
        if other is EmptyVolume:
            yield self
            return
        if self is EmptyVolume:
            yield other
            return
        if other is FullVolume or self is FullVolume:
            yield FullVolume
            return
        dimensions = []
        for self_dimension, other_dimension in zip(self, other):
            dimension = self_dimension | other_dimension
            # if isinstance(dimension, Range):
            #     dimension = OrRange((dimension,))
            dimensions.append(dimension)
        for dims in product(*dimensions):
            if not any(_dim == EmptyRange for _dim in dims):
                yield Volume(dims)

    def __contains__(self, item: Rating):
        dim_dict = self.dim_dict
        return all(value in dim_dict[dim] for dim, value in item.items())

    def replace_dimension(self: Self, dim: Dim, dim_value: Range) -> Self:
        """Return a copy of self with one of the dimension values replaced"""
        return Volume(**{**self.dim_dict, **{dim: dim_value}})

    def partition(self, dim: Dim, value: int, gt: bool) -> tuple[Self, Self]:
        """Split a volume into two: one where condition is true
        and where condition is false in the given dimension"""

        dims: dict[str, Range] = self.dim_dict
        true_dim, false_dim = dims[dim].partition(value, gt)

        return (
            (
                self.replace_dimension(dim, true_dim)
                if true_dim is not EmptyRange
                else EmptyVolume
            ),
            (
                self.replace_dimension(dim, false_dim)
                if false_dim is not EmptyRange
                else EmptyVolume
            ),
        )

    def overlaps(self, other: Self) -> bool:
        """Do self and other overlap? True if all dimensions have overlap."""
        return all(
            self_d.overlaps(other_d)
            for self_d, other_d in zip(self.dimensions, other.dimensions)
        )

    def is_disjoint(self, other: Self) -> bool:
        return not self.overlaps(other)

    def contains(self, other: Self) -> bool:
        """Is the other completely contained within (even up to
        overlapping) self?"""
        return all(
            self_d in other_d
            for self_d, other_d in zip(self.dimensions, other.dimensions)
        )

    def is_contained_by(self, other: Self) -> bool:
        return other.contains(self)

    def make_disjoint(self, other: Self) -> Iterable[Self]:
        """Compare self and other. If they overlap, break up self and
        yield non-overlapping shards until no more overlap exists.

        The way we "shard" the volume is to look through each dimension
        one by one, splitting each into non-overlapping and overlapping parts.
        For two volumes to overlap there must be overlaps in all dimensions,
        so if we split one of the dimensions into non-overlapping and overlapping parts,
        a new volume made from self but with with those ranges in that dimension
        will also be non-overlapping and overlapping, respectively, with other.

        Each of the non-overlapping volumes made from the
        successive non-overlapping dimension splits is a "shard"
        We yield each shard created in this way until, eventually all the dimensions
        in self fully overlap the dimensions in other.

        Then we return, not yielding self when it is fully contained within other.
        """
        if self.is_disjoint(other):
            # self is already disjoint with other, just keep it rolling
            yield self
            return
        if self.is_contained_by(other) or self == EmptyVolume:
            # There is nothing left that can be made disjoint
            return

        # Iterate through dimensions.
        # - Split self along the given dimension into
        #    disjoint_lower, overlap, and disjoint_upper volumes
        # - If for the given dimension there is no disjoint_lower or disjoint_upper,
        #    then self is already disjoint in this dimension. Move on to the next.
        # - If there is a disjoint_lower and/or disjoint_upper, yield them, then
        #    yield from overlap.make_disjoint(other)
        other_ds = other.dim_dict
        for d, self_d in self.dim_dict.items():
            other_d = other_ds[d]

            lower_disjoint, overlap, upper_disjoint = self_d.make_disjoint(other_d)

            if overlap == self_d:
                # There was no disjoint portion of this dimension
                assert lower_disjoint == EmptyRange
                assert upper_disjoint == EmptyRange
                continue
            if lower_disjoint != EmptyRange:
                yield self.replace_dimension(d, lower_disjoint)
            if upper_disjoint != EmptyRange:
                yield self.replace_dimension(d, upper_disjoint)
            yield from self.replace_dimension(d, overlap).make_disjoint(other)
            break  # All over dims get covered in the yield from

    @property
    def size(self):
        return prod(dim.size for dim in self.dimensions)


EmptyVolume = Volume(EmptyRange, EmptyRange, EmptyRange, EmptyRange)
FullVolume = Volume()


def parse_rating_line(line: str) -> Rating:
    if match := RATING_RE.match(line):
        return {k: int(v) for k, v in match.groupdict().items()}


Rules = dict[Result, list[Volume]]


def parse_rule(
    rule_str: str, prior_condition: Volume = FullVolume
) -> tuple[str, Volume, Volume]:
    """Parse one rule from a larger rule string.

    Any previous rules in the string may have had conditions that led to them.
    In order to read this rule, we would need to negate those conditions.
    That negation is this rule's prior condition.
    If this is the first rule, there is no prior condition, so it is the FullVolume
    (as in, every condition leads here).

    We also return the volume that negates the rule, which will be the next
    prior condition. If there is no condition on this rule, the negation is
    the empty volume.

    >>> parse_rule("pv")
    "pv", FullVolume, EmptyVolume
    >>> rule1 = parse_rule("m>838:A")
    >>> rule1
    "A", Volume(m=Range(838, RANGE_MAX)), Volume(m=Range(RANGE_MIN, 837))
    >>> parse_rule("pv", rule1[-1])
    "pv", Volume(m=Range(RANGE_MIN, 837)), EmptyVolume
    """
    condition_and_result = rule_str.split(":")
    if len(condition_and_result) == 1:
        # No explicit condition
        # Whatever is left over in the prior condition leads to this result
        # The next
        return condition_and_result[0], prior_condition, EmptyVolume

    # Partition the prior condition based on this rule's condition
    # When the condition is met, we know the result.
    # When the condition is not met, we do not yet know the result.
    condition, result_str = condition_and_result

    if match := CONDITION_RE.match(condition):
        attribute: Dim = match.group("attribute")
        value = int(match.group("value"))

        gt = match.group("comparator") == ">"

        # Whatever partition we have now is ANDed with all the ones before
        # We now know the result for another part of the range
        true_vol, false_vol = prior_condition.partition(attribute, value, gt)

        return result_str, true_vol, false_vol
    else:
        raise RuntimeError("Could not parse rule " + rule_str)


def parse_rules(rules_str: str) -> Rules:
    """Parse a rule string into a dict of Results to a list of Volumes
    leading to that result.

    >>> parse_rules("m>838:A,pv")
    {"A": [Volume(m=Range(838, RANGE_MAX))], "pv": [Volume(m=Range(RANGE_MIN, 837)]}
    """
    log.debug(f" + Parsing rules {rules_str}")

    rules: Rules = {}
    prior_condition = FullVolume
    for rule_str in rules_str.split(","):
        result, true_vol, false_vol = parse_rule(rule_str, prior_condition)

        current_conditions = rules.get(result, [])
        current_conditions.append(true_vol)
        rules[result] = current_conditions
        prior_condition = false_vol

    log.debug(" ++ Parsed rules")
    for result, volumes in rules.items():
        log.debug(f" ++++ {result}: {volumes}")

    return rules


def apply_prior_condition(workflow: Rules, prior_condition: Volume) -> Rules:
    """Given some prior condition of how we got to a workflow, apply that
    prior condition (AND) to all the conditions that come out of this workflow.

    >>> _workflow = parse_rules("m>838:A,pv")
    >>> apply_prior_condition(_workflow, Volume(a=Range(1, 2)))
    {
        "A": [Volume(m=Range(838, RANGE_MAX), a=Range(1, 2))],
        "pv": [Volume(m=Range(RANGE_MIN, 837), a=Range(1, 2)]
    }
    >>> assert apply_prior_condition(_workflow, FullVolume) == _workflow
    """
    return {
        result: [vol & prior_condition for vol in vols]
        for result, vols in workflow.items()
    }


def find_all_accept_conditions(workflows: dict[str, Rules]) -> list[Volume]:
    """Combine all the workflow rules into a disjoint set of ACCEPT conditions.

    We receive workflows, a dict mapping the workflow name to another dict of
    outcomes to conditions. Those outcomes can be other workflow names or the
    terminal conditions ACCEPT and REJECT.

    We want to begin with the special workflow IN and find all conditions
    that lead to ACCEPT, even through other workflows.
    """
    log.debug(" + Finding accept conditions")
    # Start the search with IN, no prior condition (i.e. FullVolume)
    workflow_names_and_prior_conditions = [(IN, FullVolume)]
    accept_conditions = []
    while workflow_names_and_prior_conditions:
        workflow_name, prior_condition = workflow_names_and_prior_conditions.pop()
        log.debug(
            " ++ Resolving workflow %s, prior condition %s",
            workflow_name,
            prior_condition,
        )

        # Find the workflow we are evaluating
        # Apply any prior condition we had in getting here
        workflow = apply_prior_condition(workflows.get(workflow_name), prior_condition)

        # Now dig through its results for either terminal states or
        # more workflows to look for
        for result, conditions in workflow.items():
            log.debug(" +++ Found %s, conditions %s", result, conditions)
            if result == ACCEPT:
                # Good terminal state, keep this condition
                accept_conditions.extend(conditions)
            elif result == REJECT:
                # Bad terminal state, reject this condition
                continue
            else:
                # Non-terminal state. Keep looking.
                # "result" is actually a workflow name.
                # Each condition in "conditions"
                #   becomes a prior condition for everything in that workflow.
                for condition in conditions:
                    workflow_names_and_prior_conditions.append((result, condition))

    return accept_conditions


def make_one_disjoint(volume: Volume, others: list[Volume]) -> list[Volume]:
    """Given a volume and a list of other volumes, break the volume into pieces
    such that each is either disjoint with all the others (which we keep)
    or completely overlapping with another (which we discard).
    """
    shards = [volume]
    for other in others:
        new_shards = []
        for shard in shards:
            new_shards.extend(shard.make_disjoint(other))
        shards = new_shards
    return shards


def make_all_disjoint(volumes: list[Volume]) -> list[Volume]:
    """Given a set of possibly overlapping volumes, make them all disjoint"""

    known_disjoint = []

    while volumes:
        volume = volumes.pop()
        known_disjoint.extend(make_one_disjoint(volume, volumes))
    return known_disjoint


def parse(lines: Iterable[str]) -> tuple[list[Volume], tuple[Rating, ...]]:
    lines = iter(lines)

    # Parse workflows
    workflow_tuples = []
    while line := next(lines):
        workflow_tuples.append(parse_rule_line(line))
    workflows = dict(workflow_tuples)
    log.debug(" + Found workflows %s", workflows)
    accept_conditions = find_all_accept_conditions(workflows)
    log.debug(" + Found (possibly overlapping) conditions %s", accept_conditions)

    disjoint_accept_conditions = make_all_disjoint(accept_conditions)
    log.debug(" + Found disjoint conditions %s", disjoint_accept_conditions)

    # Parse ratings
    ratings = tuple(map(parse_rating_line, lines))
    log.debug(" + Ratings: %s", ratings)

    return disjoint_accept_conditions, ratings


def parse_rule_line(line: str) -> tuple[str, Rules]:
    """Parse a workflow: a name and a line of rules"""
    name, rules_str = line[:-1].split("{")
    return name, parse_rules(rules_str)


def part_one(lines: Iterable[str]) -> int:
    disjoint_accept_conditions, ratings = parse(lines)

    return sum(
        value
        for rating in ratings
        for value in rating.values()
        if any(
            rating in accept_condition
            for accept_condition in disjoint_accept_conditions
        )
    )


def part_two(lines: Iterable[str]) -> int:
    disjoint_accept_conditions, _ = parse(lines)
    return sum(accept_condition.size for accept_condition in disjoint_accept_conditions)
