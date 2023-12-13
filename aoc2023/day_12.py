#!/usr/bin/env python
"""

PART 1
It's picross!

Given a line of empty ".", filled "#", and unknown "?" spaces,
and a check csv of sizes of contiguous regions,
count how many ways the unknown spaces could be filled and satisfy the check.

Solution discussion
One way I could do this is to go down the row, and for each unknown
try out both . and #. Check each against the checksum. If it violates
the checksum, drop it. If it satisfies, put it onto a stack.
For the next space, pop everything off the stack, try both . and #,
run the check again. Continue.

That would be feasible. But I almost want to just do the counts from first principles.
Let's spend a moment thinking about how we could do that.

Get pattern len. Total the checksum (sum numbers + len - 1 for each mandatory space)
The difference is the max number of frustrations. Actual could be smaller.
If frustrations = 0, we know the valid arrangements = 1 and can move on.

What we need is a way to reliably evaluate known good sections of the pattern
and store the parts where we still have questions. Then we could apply
our frustration calc recursively on the sections with unknowns.

Store the pattern as runs. A run has a length and a symbol.
A run also has a section of checksum that it must satisfy.
The checksum only specifies the lengths of the # runs.
We can turn a collection of runs without any ?s into a checksum
by outputting the run lengths of the # sections, omitting the . sections.

Convert . to space. Break pattern into subpatterns with strip() and split().
Assign checksum components to subpatterns. (How?)

I had to cheat. Worked on it all day, couldn't make it happen.
Shout out to reddit user Successful_Ninja4181 whose implementation I stole.
Much more successful than me, I guess.
https://www.reddit.com/r/adventofcode/comments/18ge41g/comment/kd3mplj/

PART 2
Take the input, multiply the pattern by 5 and join with ?, multiply spans by 5 too.
"""

from collections.abc import Iterable
from functools import cache


PART_ONE_EXAMPLE = """\
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
"""
PART_ONE_EXAMPLE_RESULT = 21
PART_ONE_RESULT = 6871
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 525152
PART_TWO_RESULT = 2043098029844


@cache
def get_combs(pattern: str, spans: tuple[int]) -> int:
    cur_count = spans[0]

    total = 0

    hs_pos = None

    for idx in range(len(pattern) - cur_count + 1):
        region = pattern[idx : idx + cur_count]

        # Only a valid island if it has "?" or "#"
        has_dot = "." in region

        # Over extended
        over_ext = idx + cur_count < len(pattern) and pattern[idx + cur_count] == "#"

        # Following a #
        prev_c = idx > 0 and pattern[idx - 1] == "#"

        if not (has_dot or over_ext or prev_c):
            if len(spans) == 1:
                if "#" not in pattern[idx + cur_count + 1 :]:
                    total += 1
            else:
                total += get_combs(pattern[idx + cur_count + 1 :], spans[1:])

        if hs_pos is not None and hs_pos < idx:
            break

        if hs_pos is None and "#" in region:
            hs_pos = idx + region.index("#")

    return total


def solve(line: str):
    pattern, spans = line.split(maxsplit=2)
    spans = tuple(map(int, spans.split(",")))
    return get_combs(pattern, spans)


def part_one(lines: Iterable[str]) -> int:
    return sum(map(solve, lines))


def solve2(line: str):
    pattern, spans = line.split(maxsplit=2)
    pattern = "?".join([pattern] * 5)
    spans = tuple(map(int, spans.split(",")))
    spans = (*spans, *spans, *spans, *spans, *spans)
    return get_combs(pattern, spans)


def part_two(lines: Iterable[str]) -> int:
    return sum(map(solve2, lines))
