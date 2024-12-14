#!/usr/bin/env python
"""
PART 1
Start with numbers. They update every step according to the first applicable rule:
- 0 -> 1
- if number of digits is even, split into two stones with left digits and right digits.
  (But remove leading zeros)
- multiply by 2024
How many stones do you have after 25 steps?

PART 2
Run for 75 steps.
Hope my caching is good!
(Spoiler: it was not)

Ended up hand-calculating a few rounds starting from each single digit
and getting back to a round of single digits. (Except with 8, which had
one single digit in a round of otherwise double digits because of a leading
zero. But anyway...)
I also focused on the size of the results rather than making a big list
of the actual numbers.
"""
from collections.abc import Iterable
from functools import cache

PART_ONE_EXAMPLE = """\
125 17
"""
PART_ONE_EXAMPLE_RESULT = 55312
PART_ONE_RESULT = 189092
PART_TWO_EXAMPLE = ""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 224869647102559


@cache
def step(val: int) -> tuple[int, ...]:
    if val == 0:
        return (1,)
    s_val = str(val)
    l_s_val = len(s_val)
    if l_s_val % 2 == 0:
        half = l_s_val // 2
        s_left, s_right = s_val[:half], s_val[half:]
        return int(s_left), int(s_right)
    return (val * 2024,)


def num_digits(val: int) -> int:
    return len(str(val))


@cache
def size(val: int, n: int) -> int:
    """Size of input val after n steps"""
    # Base case: no more steps, just left with val
    if n == 0:
        return 1

    # For double-or-more-digit inputs, run a step and try again
    if num_digits(val) > 1:
        return sum(size(v, n - 1) for v in step(val))

    # From here on out, all our vals are single digit.
    # If we are only taking one step, all single digit inputs go to
    #  a single output number, so the size is always 1
    if n == 1:
        return 1

    # Hard-code rule that 0 -> 1
    if val == 0:
        return size(1, n - 1)
    # 1, 2, 3, and 4 go to 1 number after 1 step, then 2 after 2,
    #  then 4 single-digit numbers after 3 steps
    # We recurse on those single-digit outputs
    elif val in (1, 2, 3, 4):
        if n == 2:
            return 2

        m = n - 3

        if val == 1:
            return 2 * size(2, m) + size(4, m) + size(0, m)
        elif val == 2:
            return 2 * size(4, m) + size(8, m) + size(0, m)
        elif val == 3:
            return sum(size(v, m) for v in (6, 0, 7, 2))
        else:
            return sum(size(v, m) for v in (8, 0, 9, 6))
    # 5, 6, 7, and 9 go to...
    # 1 step: *2024 -> 1 5-digit number
    # 2 step: *2024 -> 1 8-digit number
    # 3 step: split -> 2 4-digit numbers
    # 4 step: split -> 4 2-digit numbers
    # 5 step: split -> 8 single-digit numbers
    # We recurse on those single-digit outputs
    elif val in (5, 6, 7, 9):
        if n == 4:
            return 4
        elif n == 3:
            return 2
        elif n == 2:
            return 1

        m = n - 5
        if val == 5:
            return 2 * size(2, m) + 2 * size(0, m) + size(4, m) + 3 * size(8, m)
        elif val == 6:
            return (
                size(2, m)
                + 2 * size(4, m)
                + 2 * size(5, m)
                + size(7, m)
                + size(9, m)
                + size(6, m)
            )
        elif val == 7:
            return (
                2 * size(2, m)
                + size(8, m)
                + 2 * size(6, m)
                + size(7, m)
                + size(0, m)
                + size(3, m)
            )
        elif val == 9:
            return (
                size(3, m)
                + 2 * size(6, m)
                + 2 * size(8, m)
                + size(9, m)
                + size(1, m)
                + size(4, m)
            )
    # 8 is almost like 5, 6, 7, and 9 except for step 4
    # 1 step: *2024 -> 1 5-digit number
    # 2 step: *2024 -> 1 8-digit number
    # 3 step: split -> 2 4-digit numbers
    # 4 step: split -> 3 2-digit numbers and one 1-digit number
    # This would have been 4 2-digit numbers like the others
    #  except one has a leading zero, so becomes 1-digit.
    # We recurse on those double- and single-digit outputs
    elif val == 8:
        m = n - 4
        if n >= 4:
            return size(8, m) + size(32, m) + size(77, m) + size(26, m)
        elif n == 3:
            return 2
        else:
            return 1


def run(lines: Iterable[str], steps: int) -> int:
    return sum(size(num, steps) for num in map(int, "".join(lines).split()))


def part_one(lines: Iterable[str]) -> int:
    return run(lines, 25)


def part_two(lines: Iterable[str]) -> int:
    return run(lines, 75)
