#!/usr/bin/env python
"""
PART 1
Rules of bags in bags.
How many colors of bag could eventually contain a shiny gold bag?

PART 2
Count how many bags must be inside 1 shiny gold bag.
"""
import re
from collections.abc import Iterable
from functools import cache

PART_ONE_EXAMPLE = """\
light red bags contain 1 bright white bag, 2 muted yellow bags.
dark orange bags contain 3 bright white bags, 4 muted yellow bags.
bright white bags contain 1 shiny gold bag.
muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.
shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.
dark olive bags contain 3 faded blue bags, 4 dotted black bags.
vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.
faded blue bags contain no other bags.
dotted black bags contain no other bags.
"""
PART_ONE_EXAMPLE_RESULT = 4
PART_ONE_RESULT = 242
PART_TWO_EXAMPLE = """\
shiny gold bags contain 2 dark red bags.
dark red bags contain 2 dark orange bags.
dark orange bags contain 2 dark yellow bags.
dark yellow bags contain 2 dark green bags.
dark green bags contain 2 dark blue bags.
dark blue bags contain 2 dark violet bags.
dark violet bags contain no other bags.
"""
PART_TWO_EXAMPLE_RESULT = 126
PART_TWO_RESULT = 176035

RULE_RE = re.compile(r"(?P<outer>.*?) bags contain (?P<therest>.*)")
REST_RE = re.compile(r"(?P<digitcolor>(\d+ .*?)|(no other)) bags?\.?")


type Rules = dict[str, tuple[tuple[int, str], ...]]
EMPTY = (0, "")
SHINY_GOLD = "shiny gold"
NO_OTHER = "no other"


def parse(lines: Iterable[str]) -> Rules:
    d = {}
    for line in lines:
        if (m := RULE_RE.match(line)) is not None:
            inner = []
            for bag in m.group("therest").split(", "):
                if (n := REST_RE.match(bag)) is not None:
                    dc = n.group("digitcolor")
                    if dc == NO_OTHER:
                        inner.append(EMPTY)
                        break
                    else:
                        digit, color = dc.split(" ", maxsplit=1)
                        inner.append((int(digit), color))
                else:
                    raise ValueError(
                        "Couldn't parse the rest \"" + m.group("therest") + '"'
                    )
            d[m.group("outer")] = tuple(inner)
    return d


def part_one(lines: Iterable[str]) -> int:
    rules = parse(lines)

    @cache
    def can_contain_shiny_yellow(outer: str) -> bool:
        return any(
            num > 0 and (inner == SHINY_GOLD or can_contain_shiny_yellow(inner))
            for num, inner in rules.get(outer, (0, ""))
        )

    return sum(map(can_contain_shiny_yellow, rules.keys()))


def part_two(lines: Iterable[str]) -> int:
    rules = parse(lines)

    @cache
    def num_inside(outer: str) -> int:
        return sum(
            0 if num == 0 else num * (1 + num_inside(inner))
            for num, inner in rules.get(outer, EMPTY)
        )

    return num_inside(SHINY_GOLD)
