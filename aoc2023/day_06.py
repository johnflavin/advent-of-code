#!/usr/bin/env python
"""

PART 1
You're given a set of times and distances.
Time T is the max time per race, distance D is the distance to beat.
Speed and time trade off. By "charging" speed for more time you go faster.
Several different ways you can beat the time. Count the number.
Multiply those numbers together for each race to get the answer.

distance traveled = speed * time
Let's let t be the time you spend "charging" up your speed.
Then the time left you travel at that speed is T - t.
So distance traveled = t * (T - t), and
winning distances = -D + tT - t^2
Solving for the zeros with quadratic formula:
T/2 ± sqrt(T^2 - 4D)/2
We want the difference between those zeros:
sqrt(T^2 - 4D)
And we probably need to take the floor to make it an int, just guessing.
...Upon further inspection, that simple answer could be off by one.
We want all ints above left zero and below right zero:
floor(T/2 + sqrt(T^2 - 4D)/2) - ceiling(T/2 - sqrt(T^2 - 4D)/2)

...That's off by one. Need to add + 1 to that to get the count right.

...That's close but not quite it. When the zeros are exact ints, we
do not want to count them. Those times would tie the race, not win.
I don't know a great way to test that. I'll just say that after taking
the floor and ceiling, if the numbers didn't change, then we bump them
by one in the correct direction.

PART 2
There is actually only one race with a single time and dist number (ignore spaces).
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass
from math import ceil, floor, prod, sqrt


PART_ONE_EXAMPLE = """\
Time:      7  15   30
Distance:  9  40  200
"""
PART_ONE_EXAMPLE_RESULT = 288
PART_ONE_RESULT = 2374848
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 71503
PART_TWO_RESULT = 39132886


time_re = re.compile(r"Time:\s+(?P<numbers>\d[\s\d]*)")
dist_re = re.compile(r"Distance:\s+(?P<numbers>\d[\s\d]*)")


@dataclass
class Race:
    time: int
    dist: int

    @property
    def sqrt(self):
        return sqrt(self.time**2 - 4 * self.dist)

    @property
    def num_winning_times(self) -> int:
        sq = self.sqrt
        high, low = self.time / 2 + sq / 2, self.time / 2 - sq / 2
        fl_high = floor(high)
        cl_low = ceil(low)
        if fl_high == high:
            fl_high -= 1
        if cl_low == low:
            cl_low += 1

        return fl_high - cl_low + 1


def parse_lines(lines: Iterable[str]) -> tuple[list[int], list[int]]:
    lines = iter(lines)
    time_line = next(lines)
    dist_line = next(lines)

    if time_match := time_re.match(time_line):
        times = [int(num) for num in time_match.group("numbers").split()]
    else:
        raise Exception("Parse error: " + time_line)
    if dist_match := dist_re.match(dist_line):
        dists = list(map(int, dist_match.group("numbers").split()))
    else:
        raise Exception("Parse error: " + dist_line)

    return times, dists


def part_one(lines: Iterable[str]) -> int:
    times, dists = parse_lines(lines)
    return prod(Race(time, dist).num_winning_times for time, dist in zip(times, dists))


def part_two(lines: Iterable[str]) -> int:
    # Use the same parsing as before, just join them back together
    times, dists = parse_lines(lines)
    time = int("".join(str(time) for time in times))
    dist = int("".join(str(dist) for dist in dists))
    return Race(time, dist).num_winning_times
