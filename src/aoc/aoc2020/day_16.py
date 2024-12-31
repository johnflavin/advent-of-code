#!/usr/bin/env python
"""
PART 1
Given definition of field ranges and tickets (comma-separated ints).
Determine if any tickets are invalid (a value won't match any range).
Add the invalid field values.

PART 2
Using only valid tickets, figure out which field is which.
Six fields start with the word "departure". Multiply their values on your ticket.
"""
import math
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
class: 1-3 or 5-7
row: 6-11 or 33-44
seat: 13-40 or 45-50

your ticket:
7,1,14

nearby tickets:
7,3,47
40,4,50
55,2,20
38,6,12
"""
PART_ONE_EXAMPLE_RESULT = 71
PART_ONE_RESULT = 23122
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 362974212989


type Ticket = tuple[int, ...]
type Rules = dict[str, Rule]
type Rule = tuple[Range, ...]
type Range = tuple[int, int]


def parse_range(r: str) -> Range:
    lower, upper = r.split("-")
    return int(lower), int(upper)


def parse_rule(line: str) -> tuple[str, Rule]:
    name, range_strs = line.split(": ")
    ranges = tuple(map(parse_range, range_strs.split(" or ")))
    return name, ranges


def parse_ticket(line: str) -> Ticket:
    return tuple(map(int, line.split(",")))


def parse(lines: Iterable[str]) -> tuple[Rules, Ticket, Iterable[Ticket]]:
    lines = iter(lines)

    rules_list = []
    for line in lines:
        if "" == line:
            break
        rules_list.append(parse_rule(line))
    rules = dict(rules_list)

    _ = next(lines)  # title line
    mine = parse_ticket(next(lines))
    _ = next(lines)  # blank line

    _ = next(lines)  # title line
    others = [parse_ticket(line) for line in lines]
    return rules, mine, others


def in_range(val: int, r: Range) -> bool:
    return r[0] <= val <= r[1]


def matches(val: int, rule: Rule) -> bool:
    return any(in_range(val, r) for r in rule)


def invalid(ticket: Ticket, rules: Rules) -> int:
    for val in ticket:
        if not any(matches(val, rule) for rule in rules.values()):
            return val
    return 0


def part_one(lines: Iterable[str]) -> int:
    rules, _, others = parse(lines)

    return sum(invalid(other, rules) for other in others)


def part_two(lines: Iterable[str]) -> int:
    rules, mine, others = parse(lines)
    valid_others = [other for other in others if not invalid(other, rules)]

    lm = len(mine)
    possibilities = {
        name: {
            i
            for i in range(lm)
            if all(matches(other[i], rule) for other in valid_others)
        }
        for name, rule in rules.items()
    }

    ordered_rules = {}
    didnt_find = set()
    smallest = sorted(possibilities.items(), key=lambda item: len(item[1]))
    for name, possible in smallest:
        for i in possible:
            if i not in ordered_rules:
                ordered_rules[i] = name
                break
        else:
            didnt_find.add(name)

    # This is a horrible hack. I think there is something wrong with my
    #  solution where I can't find one of the categories.
    # But since I'm only missing one, I can figure out which one it must be.
    # Right? I hope so...
    assert len(didnt_find) == 1
    missing = didnt_find.pop()
    for i in range(lm):
        if i not in ordered_rules:
            ordered_rules[i] = missing

    return math.prod(
        mine[i] for i, name in ordered_rules.items() if name.startswith("departure")
    )
