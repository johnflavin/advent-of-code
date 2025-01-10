#!/usr/bin/env python
"""
PART 1
Chunk up a string, find num 1s * num 2s in chunk with fewest 0s.

PART 2
Apply layers top down:
2 is transparent, 1 is white, 0 is black.
Print image and find message.
"""
import itertools
import math
from collections import Counter
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
123456789012
"""
PART_ONE_EXAMPLE_RESULT = 1
PART_ONE_EXAMPLE_DIMS = (3, 2)
DIMS = (25, 6)
PART_ONE_RESULT = 1560
PART_TWO_EXAMPLE = """\
0222112222120000
"""
PART_TWO_EXAMPLE_RESULT = """\

⬛️⬜️
⬜️⬛️"""
PART_TWO_EXAMPLE_DIMS = (2, 2)
PART_TWO_RESULT = """\

⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬜️⬛️⬛️⬛️⬜️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️
⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️
⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬜️⬜️⬜️⬛️
⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬜️⬜️⬛️⬜️⬛️⬛️⬛️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️
⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️⬜️⬛️⬛️⬜️⬛️
⬛️⬜️⬜️⬛️⬛️⬛️⬜️⬜️⬜️⬛️⬛️⬜️⬜️⬛️⬛️⬛️⬜️⬜️⬛️⬛️⬜️⬛️⬛️⬜️⬛️"""


def part_one(lines: Iterable[str]) -> int:
    input_str = "".join(lines)
    dims = PART_ONE_EXAMPLE_DIMS if len(input_str) <= len(PART_ONE_EXAMPLE) else DIMS
    stride = math.prod(dims)
    counts = [Counter(layer) for layer in itertools.batched(input_str, stride)]
    min_zeros_layer_counts = min(counts, key=lambda c: c.get("0", 0))
    return min_zeros_layer_counts.get("1", 0) * min_zeros_layer_counts.get("2", 0)


def part_two(lines: Iterable[str]) -> str:
    input_str = "".join(lines)
    dims = PART_TWO_EXAMPLE_DIMS if len(input_str) <= len(PART_TWO_EXAMPLE) else DIMS
    stride = math.prod(dims)

    image = [2] * stride
    for layer in itertools.batched(map(int, input_str), stride):
        for i, layer_pixel in enumerate(layer):
            if image[i] == 2:
                image[i] = layer_pixel

    blackwhite = ("⬛️", "⬜️")
    image_str = "\n" + "\n".join(
        "".join(blackwhite[pixel] for pixel in row)
        for row in itertools.batched(image, dims[0])
    )
    return image_str
