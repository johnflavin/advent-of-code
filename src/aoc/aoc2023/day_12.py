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

Later update
Redid logic following tutorial by StaticMoose in
https://www.reddit.com/r/adventofcode/comments/18hbbxe/2023_day_12python_stepbystep_tutorial_with_bonus/

This was much more comprehensible than the other thing I copied. I could follow this.
And it was much more like my own logic that I abandoned.
I think I tried to get a bit too fancy, tried to do a bit too much at once,
where I should have stuck to a more straightforward recursion.

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


QUESTION_DOT = set("?.")


def pound(pattern: str, spans: tuple[int]):
    span = spans[0]

    # If the first is a pound, then the first n characters must be
    # able to be treated as a pound, where n is the first span number
    # If we see anything other than # or ? in the first n, it is impossible
    if "." in pattern[:span]:
        return 0

    # If the rest of the record is just the last span, then we're
    # done and there's only one possibility
    if len(pattern) == span:
        # Make sure this is the last span
        return int(len(spans) == 1)

    # Make sure the character that follows this group can be a seperator
    if pattern[span] in QUESTION_DOT:
        # It can be seperator, so skip it and reduce to the next span
        return calc(pattern[span + 1 :], spans[1:])

    # Can't be handled, there are no possibilities
    return 0


@cache
def calc(pattern: str, spans: tuple[int]) -> int:
    # Did we run out of groups? We might still be valid
    if not spans:
        # Make sure there aren't more damaged springs, if so, we're valid
        return int("#" not in pattern)

    # Remove all leading and trailing dots
    if pattern:
        pattern = pattern.strip(".")

    required_springs = sum(spans)
    if len(spans) + required_springs - 1 > len(pattern):
        # The pattern isn't long enough to hold all the spans
        return 0

    num_springs = pattern.count("#")
    if (
        num_springs > required_springs
        or num_springs + pattern.count("?") < required_springs
    ):
        # The pattern either has more springs than we should have, or
        # not enough spaces to hold the springs we should have
        return 0

    # Handle logic (and recurse) for next character in pattern
    if pattern[0] == "#":
        # Test pound logic
        out = pound(pattern, spans)
    elif pattern[0] == "?":
        # Recurse into both branches
        # When we start with a dot we are just going to remove it anyway,
        #  so we save a step by just removing the next character
        out = calc(pattern[1:], spans) + pound(pattern, spans)
    else:
        raise RuntimeError

    # print(pattern, ",".join(map(str, spans)), out)
    return out


def solve(line: str):
    pattern, spans = line.split(maxsplit=2)
    spans = tuple(map(int, spans.split(",")))
    # print("-"*10)
    return calc(pattern, spans)


def part_one(lines: Iterable[str]) -> int:
    return sum(map(solve, lines))


def solve2(line: str):
    pattern, spans = line.split(maxsplit=2)
    pattern = "?".join([pattern] * 5)
    spans = tuple(map(int, spans.split(",")))
    spans = (*spans, *spans, *spans, *spans, *spans)
    # print("-" * 10)
    return calc(pattern, spans)


def part_two(lines: Iterable[str]) -> int:
    return sum(map(solve2, lines))
