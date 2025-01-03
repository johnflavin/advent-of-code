#!/usr/bin/env python
"""
PART 1
Implement rules to match characters

PART 2
Make some of the rules more complex in a way that makes regex difficult or
impossible in general.
"""
import re
from collections.abc import Iterable
from functools import cache

# PART_ONE_EXAMPLE = """\
# 0: 4 1 5
# 1: 2 3 | 3 2
# 2: 4 4 | 5 5
# 3: 4 5 | 5 4
# 4: "a"
# 5: "b"
#
# ababbb
# bababa
# abbbab
# aaabbb
# aaaabbb
# """
# What follows is actually part 2's example, but the puzzle gave another
# "if this were in part 1" answer, and it's more complex than the example
# that had been used for part 1, so I'm going with it for both.
PART_ONE_EXAMPLE = """\
42: 9 14 | 10 1
9: 14 27 | 1 26
10: 23 14 | 28 1
1: "a"
11: 42 31
5: 1 14 | 15 1
19: 14 1 | 14 14
12: 24 14 | 19 1
16: 15 1 | 14 14
31: 14 17 | 1 13
6: 14 14 | 1 14
2: 1 24 | 14 4
0: 8 11
13: 14 3 | 1 12
15: 1 | 14
17: 14 2 | 1 7
23: 25 1 | 22 14
28: 16 1
4: 1 1
20: 14 14 | 1 15
3: 5 14 | 16 1
27: 1 6 | 14 18
14: "b"
21: 14 1 | 1 14
25: 1 1 | 1 14
22: 14 14
8: 42
26: 14 22 | 1 20
18: 15 15
7: 14 5 | 1 21
24: 14 1

abbbbbabbbaaaababbaabbbbabababbbabbbbbbabaaaa
bbabbbbaabaabba
babbbbaabbbbbabbbbbbaabaaabaaa
aaabbbbbbaaaabaababaabababbabaaabbababababaaa
bbbbbbbaaaabbbbaaabbabaaa
bbbababbbbaaaaaaaabbababaaababaabab
ababaaaaaabaaab
ababaaaaabbbaba
baabbaaaabbaaaababbaababb
abbbbabbbbaaaababbbbbbaaaababb
aaaaabbaabaaaaababaa
aaaabbaaaabbaaa
aaaabbaabbaaaaaaabbbabbbaaabbaabaaa
babaaabbbaaabaababbaabababaaab
aabbbbbaabbbaaaaaabbbbbababaaaaabbaaabba
"""
PART_ONE_EXAMPLE_RESULT = 3
PART_ONE_RESULT = 187
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 12
PART_TWO_RESULT = 392


def process(rulestrs: dict[str, str], part1: bool) -> re.Pattern:
    @cache
    def evaluate(name: str) -> str:
        if name == "8" and not part1:
            return evaluate("42") + "+"
        if name == "11" and not part1:
            # It wants me to replace 11's rule with
            #   42 31 | 42 11 31
            # In other words, <some pattern A> n times followed by
            #   <some pattern B> n times.
            # This isn't possible in general with a regex, so
            # let's just hard-code each of the first few ns
            # and hope it works.
            # Like AB | AABB | ... etc.
            # Except I'll use the regex {n} syntax for the repeats.
            a = evaluate("42")
            b = evaluate("31")
            return "(" + "|".join(f"({a}{{{i}}}{b}{{{i}}})" for i in range(1, 5)) + ")"
        rulestr = rulestrs[name]
        if len(rulestr) >= 3 and rulestr[0] == rulestr[-1] == '"':
            return rulestr[1]
        ors = rulestr.split(" | ")
        return (
            "("
            + "|".join(
                "".join(evaluate(subname) for subname in subrule.split())
                for subrule in ors
            )
            + ")"
        )

    return re.compile(rf"^{evaluate("0")}$")


def do_the_thing(lines: Iterable[str], part1: bool) -> int:
    rulestrs = {}
    for line in lines:
        if line == "":
            break
        name, rule = line.split(": ")
        rulestrs[name] = rule

    pattern = process(rulestrs, part1)

    return sum(pattern.match(line) is not None for line in lines)


def part_one(lines: Iterable[str]) -> int:
    return do_the_thing(lines, True)


def part_two(lines: Iterable[str]) -> int:
    return do_the_thing(lines, False)
