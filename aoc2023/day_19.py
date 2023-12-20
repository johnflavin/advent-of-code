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
from collections import defaultdict
from collections.abc import Callable, Iterable
from enum import Enum
from functools import cache
from itertools import groupby
from math import prod
from operator import gt, lt


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


Rating = dict[str, int]
RuleResult = bool | str | None
Rule = Callable[[Rating], RuleResult]
WorkflowResult = bool | str
Workflow = Callable[[Rating], WorkflowResult]

Range = tuple[int, int]
Range4 = tuple[Range, Range, Range, Range]
# RulePart2 = tuple[Range4, WorkflowResult]
WorkflowPart2 = dict[WorkflowResult, tuple[Range4, ...]]
# RulePart2Again = Callable[[Range4], WorkflowResult]


# Volume = tuple[Range, Range, Range, Range]
# Empty: Volume = ((0, 0), (0, 0), (0, 0), (0, 0))


class Comparator(Enum):
    GT = 0
    LT = 1


Partition = tuple[int, int, int]  # attribute index, lower bound, upper bound
AndPartition = tuple[Partition, ...]
OrPartition = tuple[AndPartition, ...]
# RuleV3 = tuple[WorkflowResult, AndPartition]


RATING_RE = re.compile(r"{x=(?P<x>\d+),m=(?P<m>\d+),a=(?P<a>\d+),s=(?P<s>\d+)}")
CONDITION_RE = re.compile(r"(?P<attribute>[xmas])(?P<comparator>[<>])(?P<value>\d+)")


RANGE_MIN = 1
RANGE_MAX = 4000
IDENTITY_RANGE4: Range4 = (
    (RANGE_MIN, RANGE_MAX),
    (RANGE_MIN, RANGE_MAX),
    (RANGE_MIN, RANGE_MAX),
    (RANGE_MIN, RANGE_MAX),
)
ATTRIBUTES: dict[str, int] = {
    "x": 0,
    "m": 1,
    "a": 2,
    "s": 3,
}


log = logging.getLogger(__name__)


@cache
def is_debug() -> bool:
    return log.isEnabledFor(logging.DEBUG)


@cache
def parse_rule_result_str(result: str) -> WorkflowResult:
    if result == "A":
        return True
    elif result == "R":
        return False
    else:
        return result


def parse_rule(rule_str: str) -> Rule:
    condition_and_result = rule_str.split(":")
    if len(condition_and_result) == 1:
        # No : means no condition, always return
        result = parse_rule_result_str(condition_and_result[0])

        def rule(_: Rating) -> RuleResult:
            if is_debug():
                log.debug(f" ++ Base case: return {result}")
            return result

        return rule
    else:
        condition, result_str = condition_and_result
        result = parse_rule_result_str(result_str)

        if match := CONDITION_RE.match(condition):
            attribute = match.group("attribute")
            comparator = gt if match.group("comparator") == ">" else lt
            value = int(match.group("value"))

            def rule(rating: Rating) -> RuleResult:
                actual_value = rating[attribute]
                comparison = comparator(actual_value, value)
                to_return = result if comparison else None
                if is_debug():
                    log.debug(
                        f" ++ {condition}:{result_str} => "
                        f"{actual_value} {comparator} {value} => "
                        f"{comparison} => {to_return}"
                    )
                return to_return

            return rule
        raise RuntimeError("Could not parse rule " + rule_str)


def parse_workflow_line(line: str) -> tuple[str, Workflow]:
    name, rule_strs = line[:-1].split("{")
    rules = [parse_rule(rule_str) for rule_str in rule_strs.split(",")]

    def workflow(rating: Rating) -> WorkflowResult:
        if is_debug():
            log.debug(f" + Workflow {name} rating {rating}")
        for rule in rules:
            rule_result = rule(rating)
            if rule_result is not None:
                if is_debug():
                    log.debug(f" + Workflow {name} result {rule_result}")
                return rule_result
        raise RuntimeError("None of the rules returned")

    return name, workflow


def parse_rating_line(line: str) -> Rating:
    if match := RATING_RE.match(line):
        return {k: int(v) for k, v in match.groupdict().items()}


def parse(lines: Iterable[str]) -> tuple[dict[str, Workflow], tuple[Rating, ...]]:
    lines = iter(lines)

    # Parse workflows
    workflow_tuples = []
    while line := next(lines):
        workflow_tuples.append(parse_workflow_line(line))
    workflows = dict(workflow_tuples)

    # Parse ratings
    ratings = tuple(map(parse_rating_line, lines))

    return workflows, ratings


# def merge_adjacent_ranges(range4_a: Range4, range4_b: Range4) -> Range4 | None:
#     log.debug(f" ++ Attemping to merge adjacent ranges {range4_a} and {range4_b}")
#     did_merge = False
#     merged = []
#     for (lower_a, upper_a), (lower_b, upper_b) in zip(range4_a, range4_b):
#         if upper_a == lower_b - 1:
#             # This is good, this is an adjacent range which we can merge
#             merged.append((lower_a, upper_b))
#             did_merge = True
#         elif upper_b == lower_a - 1:
#             # This is good, this is an adjacent range which we can merge
#             merged.append((lower_b, upper_a))
#             did_merge = True
#         elif lower_a == lower_b and upper_a == upper_b:
#             # This is fine, the ranges overlap, they can come along for the ride
#             merged.append((lower_a, upper_a))
#         else:
#             # This is bad. Can't merge
#             break
#     else:
#         # We get here if we didn't break, therefore we may have merged.
#         return tuple(merged) if did_merge else None
#     # We get here if we broke, therefore we have non-adjacent or non-identical ranges.
#     return None


# def consolidate_range4s(range4s: Iterable[Range4]) -> Iterable[Range4]:
#     range4s = list(range4s)
#     if len(range4s) < 2:
#         yield from range4s
#         return
#     log.debug(f" ++ Consolidating ranges {range4s}")
#     while range4s:
#         # Merge adjacent ranges with identical results
#         range4_a = range4s.pop()
#
#         for b_idx, range4_b in enumerate(range4s):
#             merged_range4 = merge_adjacent_ranges(range4_a, range4_b)
#             if merged_range4 is not None:
#                 log.debug(f" +++ Merged {range4_a} "
#                           f"and {range4_b} into {merged_range4}")
#                 # We got a merge
#                 # Remove old pre-merge _b
#                 del range4s[b_idx]
#                 # Add back merged _a and _b
#                 range4s.append(merged_range4)
#                 break
#         else:
#             # This _a didn't merge with anything
#             log.debug(f" +++ Cannot merge {range4_a}")
#             yield range4_a


# def consolidate_rules(rules_group: Iterable[RulePart2]) -> Iterable[RulePart2]:
#     log.debug(f" + Consolidating rules")
#     for result, rules_group in groupby(rules_group, lambda rule: rule[1]):
#         log.debug(f" ++ Consolidating {result} ranges")
#         for merged_range4 in consolidate_range4s((rg[0] for rg in rules_group)):
#             yield merged_range4, result


def insert(rating_range: Range4, a_range: Range, range_idx: int) -> Range4:
    return *rating_range[0:range_idx], a_range, *rating_range[range_idx + 1 : 5]


def split_range(
    new_lower_upper: int, lower: int, upper: int
) -> tuple[Range | None, Range | None]:
    if lower < new_lower_upper < upper:
        return (lower, new_lower_upper), (new_lower_upper + 1, upper)
    elif lower >= new_lower_upper:
        return None, (lower, upper)
    elif new_lower_upper >= upper:
        return (lower, upper), None


def merge_and_partitions(
    and_partitions: Iterable[AndPartition],
) -> Iterable[AndPartition]:
    log.debug(f" ++ Merge And Partitions {and_partitions}")
    and_partitions = sorted(and_partitions)
    for attr_idx, partition_attr_group in groupby(and_partitions, lambda p: p[0]):
        partition_attr_group = list(partition_attr_group)
        while partition_attr_group:
            partition1 = partition_attr_group.pop()
            for p2_idx, partition2 in enumerate(partition_attr_group):
                # Do they overlap?
                p1_low, p1_high = partition1[1:]
                p2_low, p2_high = partition2[1:]
                if p1_low > p2_high or p2_low > p2_high:
                    # No overlap
                    # This cannot be
                    pass
                else:
                    # There is partial or complete overlap
                    # Just merge them all the way together
                    del partition_attr_group[p2_idx]
                    partition_attr_group.append(
                        (attr_idx, min(p1_low, p2_low), max(p1_high, p2_high))
                    )
                    break
            else:
                yield partition1


def merge_or_partitions(or_partitions: Iterable[OrPartition]) -> Iterable[OrPartition]:
    log.debug(f" ++ Merge Or Partitions {or_partitions}")

    or_partitions = sorted(or_partitions)
    for attr_idx, partition_attr_group in groupby(or_partitions, lambda p: p[0]):
        partition_attr_group = list(partition_attr_group)
        while partition_attr_group:
            partition1 = partition_attr_group.pop()
            for p2_idx, partition2 in enumerate(partition_attr_group):
                # Do they overlap?
                p1_low, p1_high = partition1[1:]
                p2_low, p2_high = partition2[1:]
                if p1_low > p2_high or p2_low > p2_high:
                    # No overlap
                    pass
                else:
                    # There is partial or complete overlap
                    # Just merge them all the way together
                    del partition_attr_group[p2_idx]
                    partition_attr_group.append(
                        (attr_idx, min(p1_low, p2_low), max(p1_high, p2_high))
                    )
                    break
            else:
                yield partition1
    or_partitions = list(sorted(or_partitions))
    while or_partitions:
        or_partition1 = or_partitions.pop()
        if or_partitions:
            # or_partition2 = or_partitions.pop()
            # or1_segments = []
            # or2_segments = []
            for attr_idx in ATTRIBUTES.values():
                or1_attr_group = [
                    or_part1 for or_part1 in or_partition1 if or_part1[0] == attr_idx
                ]
                # or2_attr_group = [
                #     or_part2 for or_part2 in or_partition2 if or_part2[0] == attr_idx
                # ]
                if not or1_attr_group:
                    # if they overlap...
                    # Cut them up into non-overlapping segments
                    # Put all the segments back into partitions
                    #
                    ...
            ...
        else:
            yield or_partition1


def parse_rulev3(rules_str: str) -> dict[WorkflowResult, OrPartition]:
    log.debug(f" + Parsing rules {rules_str}")

    rules: dict[WorkflowResult, list[AndPartition]] = defaultdict(default_factory=list)
    partition_buffer = []
    for rule_str in rules_str.split(","):
        condition_and_result = rule_str.split(":")
        if len(condition_and_result) == 1:
            # Whatever is left over in the unknown range leads to this result
            result = parse_rule_result_str(condition_and_result[0])

            rules[result].append(tuple(partition_buffer))
        else:
            # Partition the unknown range based on the condition
            # When the condition is met, we know the result.
            # When the condition is not met, we do not yet know the result.
            condition, result_str = condition_and_result
            result = parse_rule_result_str(result_str)

            if match := CONDITION_RE.match(condition):
                attribute = match.group("attribute")
                range_idx = ATTRIBUTES[attribute]
                value = int(match.group("value"))

                if match.group("comparator") == ">":
                    partition = (range_idx, value + 1, RANGE_MAX)
                    inverse_partition = (range_idx, RANGE_MIN, value)
                else:
                    partition = (range_idx, RANGE_MIN, value - 1)
                    inverse_partition = (range_idx, value, RANGE_MAX)

                # Whatever partition we have now is ANDed with all the ones before
                # We now know the result for another part of the range
                rules[result].append((*partition_buffer, partition))

                # Add the inverse of this partition to the buffer for the next rule
                partition_buffer.append(inverse_partition)
            else:
                raise RuntimeError("Could not parse rule " + rule_str)

    log.debug(" ++ Parsed rules")
    log.debug(" +++ Before merging:")
    for result, or_partitions in rules.items():
        log.debug(f" ++++ {result} {or_partitions}")

    # merged_and_rules = {
    #     result: tuple(or_partitions) for result, or_partitions in rules.items()
    # }


def parse_rule2(rules_str: str) -> dict[WorkflowResult, tuple[Range4, ...]]:
    log.debug(f" + Parsing rules {rules_str}")
    range4_unknown_result = IDENTITY_RANGE4

    rules: dict[WorkflowResult, list[Range4]] = defaultdict(default_factory=list)
    for rule_str in rules_str.split(","):
        condition_and_result = rule_str.split(":")
        if len(condition_and_result) == 1:
            # Whatever is left over in the unknown range leads to this result
            result = parse_rule_result_str(condition_and_result[0])
            rules[result].append(range4_unknown_result)
        else:
            # Partition the unknown range based on the condition
            # When the condition is met, we know the result.
            # When the condition is not met, we do not yet know the result.
            condition, result_str = condition_and_result
            result = parse_rule_result_str(result_str)

            if match := CONDITION_RE.match(condition):
                attribute = match.group("attribute")
                range_idx = ATTRIBUTES[attribute]
                value = int(match.group("value"))

                # Split whichever range component this rule is about
                split_range1, split_range2 = split_range(
                    value - 1, *range4_unknown_result[range_idx]
                )
                if match.group("comparator") == ">":
                    known_range = split_range2
                    unknown_range = split_range1
                else:
                    known_range = split_range1
                    unknown_range = split_range2

                if known_range is None:
                    # This rule didn't provide us any new information
                    continue

                # We now know the result for another part of the range
                new_known_result_range = insert(
                    range4_unknown_result, known_range, range_idx
                )
                rules[result].append(new_known_result_range)

                if unknown_range is None:
                    # We have fully partitioned all the rules using these ranges
                    break
                # The remaining range still has an unknown result
                range4_unknown_result = insert(
                    range4_unknown_result, unknown_range, range_idx
                )
            else:
                raise RuntimeError("Could not parse rule " + rule_str)

    log.debug(" ++ Got rules")
    for result, ranges in rules.items():
        log.debug(f" +++ {result} {ranges}")

    return {result: tuple(ranges) for result, ranges in rules.items()}


def parse_part_two(lines: Iterable[str]) -> dict[str, WorkflowPart2]:
    lines = iter(lines)

    # Parse workflows
    workflow_tuples = []
    while line := next(lines):
        workflow_tuples.append(parse_workflow_line_part_two(line))
    return dict(workflow_tuples)


def parse_workflow_line_part_two(line: str) -> tuple[str, WorkflowPart2]:
    name, rules_str = line[:-1].split("{")
    return name, parse_rule2(rules_str)


def parse_workflow_line_part_two_v3(line: str) -> tuple[str, WorkflowPart2]:
    name, rules_str = line[:-1].split("{")
    return name, parse_rulev3(rules_str)


def range_size(a_range: Range) -> int:
    return a_range[1] - a_range[0] + 1


def ranges_size(rating_range: Range4) -> int:
    return prod(map(range_size, rating_range))


def rate(rating: Rating, workflows: dict[str, Workflow]) -> int:
    accept = None
    workflow = workflows["in"]
    while accept is None:
        workflow_result = workflow(rating)
        if isinstance(workflow_result, bool):
            accept = workflow_result
        else:
            workflow = workflows[workflow_result]

    return sum(rating.values()) if accept else 0


def part_one(lines: Iterable[str]) -> int:
    workflows, ratings = parse(lines)
    return sum(rate(rating, workflows) for rating in ratings)


def part_two(lines: Iterable[str]) -> int:
    workflows = parse_part_two(lines)
    # print(workflows)
    ranges_by_result = workflows["in"]

    while ranges_by_result:
        # if True in ranges_by_result:
        #     accepted = consolidate_ranges(accepted, ranges_by_result.pop(True))
        # if False in ranges_by_result:
        #     _ = ranges_by_result.pop(False)

        new_ranges_by_result: dict[str, set[Range4]] = defaultdict(default_factory=set)
        for result_or_workflow_name, range4s in ranges_by_result.items():
            log.debug(f" + Result {result_or_workflow_name} range4s {range4s}")
            if isinstance(result_or_workflow_name, str):
                # This result points to another workflow
                # Grab all its ranges and intersect them into these ranges
                a_workflow_ranges_by_result = workflows[result_or_workflow_name]
                # print(f" + Merging {rule_to_merge}")
                for (
                    a_workflow_result,
                    a_workflow_range4s,
                ) in a_workflow_ranges_by_result.items():
                    if a_workflow_result is False:
                        continue
                    log.debug(
                        f" ++ Intersecting workflow "
                        f"{result_or_workflow_name}'s "
                        f"{a_workflow_result} result range4s "
                        f"{a_workflow_range4s}"
                    )
                    log.debug(
                        f" ++ Beginning merge of workflow "
                        f"{result_or_workflow_name}'s "
                        f"{a_workflow_result} result ranges"
                    )

                    new_ranges_by_result[a_workflow_result].update()

            for a_workflow_results, range4_b in workflows[
                result_or_workflow_name
            ].items():
                new_ranges_by_result[a_workflow_results].append()

        ranges_by_result = new_ranges_by_result
        # range_to_resolve, result_to_resolve = rule_to_resolve

    # log.debug("accepted range4s")
    # for range4_a in accepted_ranges:
    #     log.debug(range4_a)

    # return sum(map(ranges_size, consolidate_range4s(accepted_ranges)))
    return -1
