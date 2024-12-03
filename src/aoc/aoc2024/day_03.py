#!/usr/bin/env python
"""
PART 1
Find all sequences that look like "mul(x,y)", multiply them, and sum

PART 2
Now only use "mul(x,y)" instructions if we are enabled by a "do()",
which is disabled by a "don't()".
"""
import logging
import re
from collections.abc import Iterable

from aoc.util import Range


PART_ONE_EXAMPLE = """\
xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))
"""
PART_ONE_EXAMPLE_RESULT = 161
PART_ONE_RESULT = 173517243
PART_TWO_EXAMPLE = """\
xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
"""
PART_TWO_EXAMPLE_RESULT = 48
PART_TWO_RESULT = 100450138


MUL_RE = re.compile(r"mul\((?P<x>\d+),(?P<y>\d+)\)")


log = logging.getLogger(__name__)


def find_muls(line: str) -> int:
    log.debug("find_muls %s", line)
    return sum(int(m.group("x")) * int(m.group("y")) for m in MUL_RE.finditer(line))


def part_one(lines: Iterable[str]) -> int:
    # Not sure if there are multiple lines, but if there are, let's make one
    return find_muls("".join(lines))


def part_two(lines: Iterable[str]) -> int:
    line = "".join(lines)

    def find_enabled_ranges() -> Iterable[Range]:
        do_i = 0
        dont_i = -1
        for m in re.finditer(r"do(n't)?\(\)", line):
            is_enabled = do_i > dont_i
            match = m.group()
            log.debug(
                "is_enabled=%s do_i=%d dont_i=%d m.group()=%s",
                is_enabled,
                do_i,
                dont_i,
                match,
            )

            if is_enabled and match == "don't()":
                dont_i = m.start()
                yield Range(do_i, dont_i)
            elif match == "don't()":
                dont_i = m.start()
            elif not is_enabled and match == "do()":
                do_i = m.start()
        # Catch case where we have a do() but no matching don't() by the end
        if do_i > dont_i:
            yield Range(do_i, len(line))

    return sum(find_muls(line[r.lower : r.upper]) for r in find_enabled_ranges())
