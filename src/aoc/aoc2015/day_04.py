#!/usr/bin/env python
"""
PART 1
Start with a "secret key"
Find the lowest integer such that when you append it to the key,
the MD5 hash starts with five zeros.

PART 2
Now find hashes starting with six zeros
"""
import hashlib
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
pqrstuv
"""
PART_ONE_EXAMPLE_RESULT = 1048970
PART_ONE_RESULT = 254575
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = 1038736


def find_hash(key: str, zero_length: int, init: int = 0) -> int:
    zeros = "0" * zero_length
    i = init
    while True:
        md5_hash = hashlib.md5(f"{key}{i}".encode()).hexdigest()
        if md5_hash[:zero_length] == zeros:
            break
        i += 1
    return i


def part_one(lines: Iterable[str]) -> int:
    key = list(lines)[0]
    return find_hash(key, 5)


def part_two(lines: Iterable[str]) -> int:
    key = list(lines)[0]
    return find_hash(key, 6, PART_ONE_RESULT)
