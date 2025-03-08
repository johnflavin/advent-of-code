#!/usr/bin/env python
"""
PART 1

PART 2
"""
import itertools
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
80871224585914546619083218645595"""
PART_ONE_EXAMPLE_RESULT = 24176176
PART_ONE_RESULT = 25131128
PART_TWO_EXAMPLE = """\
03036732577212944063491565474664"""
PART_TWO_EXAMPLE_RESULT = 84462026
PART_TWO_RESULT = 53201602


KERNEL = [0, 1, 0, -1]


def part_one(lines: Iterable[str]) -> int:
    def fft(inp: list[int]) -> list[int]:
        outp = []
        for i in range(1, len(inp) + 1):
            # Expand kernel
            kernel = itertools.chain.from_iterable(
                itertools.repeat(k, i) for k in KERNEL
            )
            # Make an iterator that goes forever
            k_iter = itertools.cycle(kernel)
            # Drop the first element
            next(k_iter)

            # Perform the operation
            outp_val = sum(inp_v * k for inp_v, k in zip(inp, k_iter))

            # Keep only the ones-digit
            outp.append(abs(outp_val) % 10)
        return outp

    input_ = [int(i) for i in "".join(lines)]
    for i in range(100):
        input_ = fft(input_)
    return sum(10 ** (7 - i) * x for i, x in enumerate(input_[:8]))


def part_two(lines: Iterable[str]) -> int:
    input_ = [int(i) for i in "".join(lines)] * 10_000
    offset = sum(10 ** (6 - i) * x for i, x in enumerate(input_[:7]))

    # In the second half of the input sequence,
    # (which the offset will be chosen to give us)
    # the coefficients are just one from a given digit to the end.
    # A number in the output sequence will be the cumulative sum
    # from that input digit to the end.

    # Keep the last $offset and reverse the sequence
    seq = reversed(input_[offset:])

    # Take 100 cumulative sums (mod 10)
    for _ in range(100):
        seq = [s % 10 for s in itertools.accumulate(seq)]

    # Read off the last 8 digits
    return sum(digit * 10**i for i, digit in enumerate(seq[-8:]))
