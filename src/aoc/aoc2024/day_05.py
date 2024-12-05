#!/usr/bin/env python
"""
PART 1
Given ordering rules X|Y (X is before Y) and
candidate ordered sets, first reject any incorrectly
ordered sets, then add the middle elements of correctly
ordered sets.

PART 2
Put the incorrectly ordered sets into the correct order
and add their middle elements
"""
import logging
from collections import defaultdict
from collections.abc import Iterable
from functools import cmp_to_key

PART_ONE_EXAMPLE = """\
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47
"""
PART_ONE_EXAMPLE_RESULT = 143
PART_ONE_RESULT = 4569
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 123
PART_TWO_RESULT = 6456

log = logging.getLogger(__name__)


def find_middle_element(candidate: list[str]) -> int:
    middle_idx = len(candidate) // 2
    middle = int(candidate[middle_idx])
    log.debug("candidate[%d] = %d", middle_idx, middle)
    return middle


def parse_rules(lines: Iterable[str]) -> dict[str, set[str]]:
    """Parse an iterable of X|Y lines into {X: {Y, ...}, ...}"""
    pairs = [line.split("|") for line in lines]

    # Make a dict of a label mapped to
    # everything it is greater than
    rules = defaultdict(set)
    for left, right in pairs:
        rules[left].add(right)
    if log.isEnabledFor(logging.DEBUG):
        for k, v in sorted(rules.items(), key=lambda item: item[0]):
            log.debug("%s > %s", k, sorted(v))

    return rules


def sort_candidate(
    candidate: list[str], rules: dict[str, set[str]], reverse: bool = False
) -> list[str]:
    """Reorder a list of strings according to the rules

    Use the built-in sorted function with a custom comparison function
    that determines which element is greater by whether it is in the other
    element's set or vice-versa.
    Then convert that comparison function to a key function using
    functools.cmp_to_key for use in sorted(..., key=key_func)"""

    def comp(a: str, b: str) -> int:
        """Compare a and b. Return -1 if a < b, 0 if a == b, 1 if a > b"""
        if b in rules[a]:
            return 1
        elif a in rules[b]:
            return -1
        elif a == b:
            return 0
        else:
            raise RuntimeError("Cannot compare %s and %s", a, b)

    return sorted(candidate, key=cmp_to_key(comp), reverse=reverse)


def part_one(lines: Iterable[str]) -> int:
    pair_lines = []
    candidate_lines = []
    accumulator = pair_lines
    for line in lines:
        if not line:
            accumulator = candidate_lines
            continue
        accumulator.append(line)

    rules = parse_rules(pair_lines)

    candidates = [line.split(",") for line in candidate_lines]
    return sum(
        find_middle_element(candidate)
        for candidate in candidates
        if sort_candidate(candidate, rules) == candidate
        or sort_candidate(candidate, rules, reverse=True) == candidate
    )


def part_two(lines: Iterable[str]) -> int:
    pair_lines = []
    candidate_lines = []
    accumulator = pair_lines
    for line in lines:
        if not line:
            accumulator = candidate_lines
            continue
        accumulator.append(line)

    rules = parse_rules(pair_lines)

    candidates = [line.split(",") for line in candidate_lines]
    return sum(
        find_middle_element(sorted_candidate)
        for candidate in candidates
        if (sorted_candidate := sort_candidate(candidate, rules)) != candidate
        and sort_candidate(candidate, rules, reverse=True) != candidate
    )
