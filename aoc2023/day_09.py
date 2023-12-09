#!/usr/bin/env python
"""

PART 1
Input is a sequence of numbers on each line.
For each sequence, take the difference between pairs of numbers
 to generate a new sequence. Eventually all the diffs will be zero.
 By reversing that process, we will be able to add another number to
 the previous non-zero sequence (which will have all identical entries),
 and the sequence before that (which will be linearly increasing)
 and so on until we are back to the original sequence
 and have added another entry.
Note: I think you're tempted to use recursion here, but don't.
 I'm guessing the inputs will be so big that we would have to recurse
 too many times and overflow the stack.

Find the next value for each sequence and add them together.

Solution notes:
Pairwise subtract all the sequence elements,
storing the new sequence each time, until we get to an all-zero sequence.
At each step we store the initial value of the previous sequence, which will
let us bootstrap that sequence on the way back up.
Starting with our all-zero sequence (to which we add one more zero)
we use itertools.accumulate to pairwise add all the sequence values,
starting with the initial value at each level, to generate the next sequence.

Do that until we have run out of initial values.
We should be back up at the starting sequence, which should have a new value.
Read that off and we're done with that sequence.

PART 2
Same sequences, but now we are generating new zeroth values on the left.

Seems like this will actually be easier than the first, since all we need
at the end is the previous and current initial values.
"""

from collections.abc import Iterable
from itertools import accumulate, pairwise, starmap


PART_ONE_EXAMPLE = """\
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
"""
PART_ONE_EXAMPLE_RESULT = 114
PART_ONE_RESULT = 1647269739
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 2
PART_TWO_RESULT = 864


def revsub(one: int, two: int) -> int:
    return two - one


def reduce(seq: list[int]) -> tuple[list[int], list[int]]:
    """Reduce a sequence down through repeated pairwise subtractions
    Return the sequence of initial values all the way down,
    and the sequence of zeros that remains."""
    initial_values = []
    while any(seq):
        initial_values.append(seq[0])
        seq = list(starmap(revsub, pairwise(seq)))
    return initial_values, seq


def predict_next(seq: list[int]) -> int:
    """
    Reduce a sequence through pairwise subtractions, keeping track of initial values.
    Eventually the sequence will be all zeros.
    Add a new zero to the end.
    Then reverse the process, pairwise adding the sequence values to
    each initial value to generate a new sequence.

    Exhaust all the initial values until we have regenerated the starting sequence
    with a new value.

    Return that new value.
    """
    initial_values, seq = reduce(seq)

    seq.append(0)

    for initial in reversed(initial_values):
        seq = list(accumulate(seq, initial=initial))

    return seq[-1]


def predict_previous(seq: list[int]) -> int:
    """
    Reduce a sequence through pairwise subtractions, keeping track of initial values.
    Eventually the sequence will be all zeros.

    Generate a new zeroth value at each sequence level
    by subtracting the stored initial value from the previous sequence's
    zeroth value (starting with the zeroth value 0 for the all-zero sequence).
    Continue until all initial values are exhausted.

    Return the zeroth value of the starting sequence.
    """
    initial_values, _ = reduce(seq)
    return list(accumulate(reversed(initial_values), func=revsub))[-1]


def part_one(lines: Iterable[str]) -> int:
    return sum(predict_next([int(st) for st in line.split()]) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    return sum(predict_previous([int(st) for st in line.split()]) for line in lines)
