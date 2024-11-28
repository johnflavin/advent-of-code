#!/usr/bin/env python
"""

PART 1

Calculate a hash of a string:
Initialize to value 0
Loop over characters in the string
- Add ASCII code of character to current value
- Multiply by 17
- Keep the remainder of division by 256

Solution notes
I'm pretty sure I can delay the mod 256 until the end. At least I'll try it that way.
I will keep multiplying by 17 each time, but I think there is probably a better way
    to do that part too.
Whatever, I don't need to optimize it too much, especially given that
    part 2 will almost certainly have me interpret the strings differently and
    do different stuff to them.

PART 2
Parse out each segment of the csv string.
First part is the "label".
Hash the label to get a box number. (Note: start caching hashes)
Label will be followed by a "=" or a "-"
- "-" means remove the lens with that label from the box if it exists
- "=" will be followed by a number: the focal length of the lens to put into the box.
    - If there is already a lens in the box with that label, replace it (in place)
    - If there is not a lens in the box with the label, put it in behind all others

To get answer, sum the "focusing power" of each lens.
(box number + 1) * (lens position + 1) * lens focal length

Solution discussion
Boxes are an array of length 256.
But for each item we need to do a couple different operations:
- We need to do lookups based on the label (remove lens with a label)
- We need to keep track of order of the lenses

I think a python dict can do that natively. It keeps track of insertion order of
keys, and updates don't change that.
I think we're good with an array of dicts.
"""

from collections.abc import Iterable
from functools import cache, reduce


PART_ONE_EXAMPLE = """\
rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7
"""
PART_ONE_EXAMPLE_RESULT = 1320
PART_ONE_RESULT = 509152
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 145
PART_TWO_RESULT = 244403


def hash_next(value: int, ch: str) -> int:
    return (value + ord(ch)) * 17


@cache
def hash_segment(segment: str) -> int:
    return reduce(hash_next, segment, 0) % 256


def focusing_power(box: dict[str, str]) -> int:
    return sum(
        (1 + idx) * int(focal_length) for idx, focal_length in enumerate(box.values())
    )


def part_one(lines: Iterable[str]) -> int:
    line = next(iter(lines))
    return sum(map(hash_segment, line.split(",")))


def part_two(lines: Iterable[str]) -> int:
    line = next(iter(lines))
    segments = line.split(",")
    boxes = [{} for _ in range(256)]
    for segment in segments:
        label, operator, focal_length = segment.partition("=")
        if operator:
            # process =
            boxes[hash_segment(label)][label] = focal_length
        else:
            # process -
            label, operator, _ = segment.partition("-")
            box = boxes[hash_segment(label)]
            if label in box:
                del box[label]

    return sum((1 + box_num) * focusing_power(box) for box_num, box in enumerate(boxes))
