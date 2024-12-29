#!/usr/bin/env python
"""
PART 1
Apply bit masks to values and write to memory

PART 2
Now the bit masks are applied to the memory addresses.
And where before X was ignored, now X takes on all values.
"""
import logging
import re
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X
mem[8] = 11
mem[7] = 101
mem[8] = 0
"""
PART_ONE_EXAMPLE_RESULT = 165
PART_ONE_RESULT = 9628746976360
PART_TWO_EXAMPLE = """\
mask = 000000000000000000000000000000X1001X
mem[42] = 100
mask = 00000000000000000000000000000000X0XX
mem[26] = 1
"""
PART_TWO_EXAMPLE_RESULT = 208
PART_TWO_RESULT = 4574598714592

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)

MEM_RE = re.compile(r"mem\[(?P<addr>\d+)] = (?P<value>\d+)")


DEFAULT_AND_MASK = (1 << 36) - 1
DEFAULT_OR_MASK = 0


def part_one(lines: Iterable[str]) -> int:
    def parse_mask(maskstr: str) -> tuple[int, int]:
        a = DEFAULT_AND_MASK
        o = DEFAULT_OR_MASK

        for i, c in enumerate(reversed(maskstr)):
            if c == "X":
                continue
            if c == "1":
                o += 1 << i
            else:
                a -= 1 << i

        return a, o

    # will set any 0 bits to 0
    and_mask = DEFAULT_AND_MASK
    # Will set any 1 bits to 1
    or_mask = DEFAULT_OR_MASK

    mem = {}
    for line in lines:
        if line[:7] == "mask = ":
            and_mask, or_mask = parse_mask(line[7:])
            if is_debug:
                log.debug(f"set masks and={and_mask:035b} or={or_mask:035b}")
        elif (m := MEM_RE.match(line)) is not None:
            mem_addr = int(m.group("addr"))
            value = int(m.group("value"))
            if is_debug:
                log.debug(f"Raw mem[{mem_addr}] = {value:035b}")

            mem[mem_addr] = (value & and_mask) | or_mask
            if is_debug:
                log.debug(f"Wrote mem[{mem_addr}] = {mem[mem_addr]:035b}")

        else:
            raise ValueError('Cannot parse line "' + line + '"')

    return sum(mem.values())


def part_two(lines: Iterable[str]) -> int:
    def parse_mask(maskstr: str) -> list[tuple[int, int]]:
        ms = [(DEFAULT_AND_MASK, DEFAULT_OR_MASK)]

        for i, c in enumerate(reversed(maskstr)):
            if c == "0":
                continue
            if c == "1":
                ms = [(a, o + (1 << i)) for a, o in ms]
            else:
                bit = 1 << i
                new_masks = []
                for a, o in ms:
                    # Write a mask where the X forces a 0
                    new_masks.append((a - bit, o))
                    # Write another mask where the X forces a 1
                    new_masks.append((a, o + bit))
                ms = new_masks

        return ms

    masks = [(DEFAULT_AND_MASK, DEFAULT_OR_MASK)]

    mem = {}
    for line in lines:
        if line[:7] == "mask = ":
            masks = parse_mask(line[7:])
        elif (m := MEM_RE.match(line)) is not None:
            mem_addr = int(m.group("addr"))
            value = int(m.group("value"))

            for and_mask, or_mask in masks:
                masked_mem_addr = (mem_addr & and_mask) | or_mask
                if is_debug:
                    log.debug(f"Writing {value} to {masked_mem_addr:035b}")

                mem[masked_mem_addr] = value

        else:
            raise ValueError('Cannot parse line "' + line + '"')

    return sum(mem.values())
