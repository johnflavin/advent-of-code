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
"""

import logging
import re
from collections.abc import Callable, Iterable
from functools import cache
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
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None


Rating = dict[str, int]
RuleResult = bool | str | None
Rule = Callable[[Rating], RuleResult]
WorkflowResult = bool | str
Workflow = Callable[[Rating], WorkflowResult]

RATING_RE = re.compile(r"{x=(?P<x>\d+),m=(?P<m>\d+),a=(?P<a>\d+),s=(?P<s>\d+)}")
CONDITION_RE = re.compile(r"(?P<attribute>[xmas])(?P<comparator>[<>])(?P<value>\d+)")


log = logging.getLogger(__name__)


@cache
def is_debug() -> bool:
    return log.isEnabledFor(logging.DEBUG)


@cache
def parse_rule_result_str(result: str) -> RuleResult:
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
    # thing = (line for line in lines if line)
    return -1
