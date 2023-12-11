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

PART 3
This is a part I'm adding myself.
Seeing the solution to part 2 made me reconsider part 1.
In part 2, all we really needed were the first elements of the sequence, right?
At least on the way back up.
That same logic applies to part 1. All we really need on the way back up
are the final elements of the sequence.
Everything in the middle is just wasted.
Well, not necessarily everything. We don't need it until we do.

Let's walk through a couple rows of the efficient calculation.
We start with a sequence of numbers.
We want to know the final element of the next sequence down.
To get that, we only need the last two numbers of the first sequence.
If that results in zero, we're done.
If not, we need to get the last element of another layer down.
But that one requires the last two of the sequence above, which depends on
elements -3 and -2 of the top sequence.
The only new thing we are bringing in is element -3 from the first sequence.
Everything else was already there.
This holds in general. To create another layer down, we bring in one more element
    from the input sequence. Reduce it through all the elements we generated last
    time to make a new sequence that is one element longer.
If you think of the input sequence as a row, and each new sequence generated by
    going across as another layer down, then what we're doing in this new method
    is generating sequences along the diagonals.

This will get us the answer with the minimum number of calculations.

Now, I know this process will work for part 1.
And I also know the same kind of thing will work for part 2
    with a small number of tweaks.
But I haven't thought through those tweaks completely yet.
Do I just flip the input sequence and everything else is the same?
Do I also need to flip something about the reduction calculation along the diagonals?
Not sure. But I'll get there.

(time jump)
Ok, I have done all the stuff I said above. And I know I'm close.
The issue is how to know when we are done.
How do we know when we can stop making new diagonals and just go back up the chain?
I had used the condition that if the new "left" diagonal ended in a zero, we have
    reached the bottom layer and can stop.
But that isn't getting me the correct answer.
I was assuming all positive values in the sequences. And looking at the inputs,
    that assumption doesn't hold.
So what to do? I think that if we generate one additional diagonal and verify that
    it ends in two zeros, that will be enough.
(This is also an assumption, though. I'm trying to avoid doing work we don't have to
    do. Technically, the problem statement said we need to know that the entire
    bottom layer is all zeros. I can't check that without generating the whole bottom
    layer. And I won't generate the whole bottom layer in this method because
    that would require me to do all the calculations which is what I'm trying to avoid.)
It's possible that some of the examples are chosen to be completely pathological
    and do require me to use all the input data and do all the calculations.
I hope not, though.
If I try this and it doesn't work, I'll give up and go back to the old method.

...It worked.
Again, it doesn't technically cover all cases, but it is enough for my input data.

I adapted things for part two. It works for the example, but fails on the full
    data set.
I think I'm going to back out of this approach.
I do like it, it could be efficient and avoid unnecessary calculations,
    but in general it's hard to tell when we are able to stop.

I think I'll go back to the "work across the layers" method, where we do
    every calculation in the reduction phase.
But I'll make the generation phase more efficient in part one.
"""

from .util import revsub
from collections.abc import Iterable
from enum import Enum
from itertools import accumulate, pairwise, starmap
from operator import add


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


class Direction(Enum):
    PREV = 0
    NEXT = -1


def reduce(seq: list[int], diag: Direction) -> Iterable[int]:
    """
    Reduce a sequence down through repeated pairwise subtractions

    For all the sequences thus generated, we collect the values along
    one of the outer diagonals: left or right.
    We return this diagonal sequence (reversed)
    """
    diag_seq = []
    while any(seq):
        diag_seq.append(seq[diag.value])
        seq = list(starmap(revsub, pairwise(seq)))
    yield from reversed(diag_seq)


def predict(seq: list[int], diag: Direction) -> int:
    expansion_op = add if diag == Direction.NEXT else revsub
    return list(accumulate(reduce(seq, diag), func=expansion_op))[-1]


def predict_all(lines: Iterable[str], direction: Direction) -> int:
    return sum(predict(list(map(int, line.split())), direction) for line in lines)


def part_one(lines: Iterable[str]) -> int:
    return predict_all(lines, Direction.NEXT)


def part_two(lines: Iterable[str]) -> int:
    return predict_all(lines, Direction.PREV)
