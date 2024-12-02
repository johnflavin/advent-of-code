#!/usr/bin/env python
"""
PART 1
Find how many strings are "nice"
- Contains at least three vowels (aeiou only)
- Contains at least one letter that appears twice in a row (aa, bb, ..., zz)
- Does not contain any of ab, cd, pq, or xy

PART 2
Find how many strings are "nice"
- Contains a pair of letters that appears twice without overlap
- Contains a letter that repeats across a gap, like ._.
"""
import itertools
import logging
import string
from collections import Counter, defaultdict, deque
from collections.abc import Iterable

import aoc.util


PART_ONE_EXAMPLE = """\
ugknbfddgicrmopn
aaa
jchzalrnumimnmhp
haegwjzuvuyypxyu
dvszwmarrgswjxmb
"""
PART_ONE_EXAMPLE_RESULT = 2
PART_ONE_RESULT = 255
PART_TWO_EXAMPLE = """\
qjhvhtzxzqqjkmpb
xxyxx
uurcxstgmygtbstg
ieodomkazucvgmuy
aaa
ugknbfddgicrmopn
jchzalrnumimnmhp
dvszwmarrgswjxmb
"""
PART_TWO_EXAMPLE_RESULT = 2
PART_TWO_RESULT = None


VOWELS = "aeiou"
NAUGHTY_PAIRS = (
    ("a", "b"),
    ("c", "d"),
    ("p", "q"),
    ("x", "y"),
)

log = logging.getLogger(__name__)


def sliding_window(iterable, n):
    """Collect data into overlapping fixed-length chunks or blocks."""
    # sliding_window('ABCDEFG', 4) → ABCD BCDE CDEF DEFG
    iterator = iter(iterable)
    window = deque(itertools.islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)


def is_nice_part_one(line: str) -> bool:
    single_counts = Counter(line)

    # Has three vowels
    num_vowels = sum(single_counts.get(v, 0) for v in VOWELS)

    if num_vowels < 3:
        return False

    double_counts = Counter(itertools.pairwise(line))

    # Has a double letter
    has_at_least_one_double_letter = any(
        (letter, letter) in double_counts for letter in string.ascii_lowercase
    )
    if not has_at_least_one_double_letter:
        return False

    # Does not have a naughty pair
    return all(naughty not in double_counts for naughty in NAUGHTY_PAIRS)


def is_nice_part_two(line: str) -> bool:
    log.debug("---")
    log.debug("Input %s", line)
    bigrams: dict[tuple[str, str], list[int]] = defaultdict(list)
    log.debug("Bigrams")
    # Now look through the bigrams to see if any occur more than once
    #  and, if so, are they non-overlapping
    for i, bigram in enumerate(sliding_window(line, 2)):
        bigrams[bigram].append(i)
        log.debug("%s %s", bigram, bigrams[bigram])

        if len(bigrams[bigram]) < 2:
            # Bigram only appears once
            # log.debug("%s Only appears once", aoc.util.FAILURE_EMOJI)
            continue
        if all(b - a == 1 for a, b in itertools.pairwise(bigrams[bigram])):
            # Instances of bigram overlap
            log.debug("%s Instances overlap", aoc.util.FAILURE_EMOJI)
            continue
        # Bigram is good
        log.debug("%s Looks good", aoc.util.SUCCESS_EMOJI)
        break
    else:
        # All bigrams are bad
        log.debug(
            "%s%s%s NAUGHTY All bigrams are bad",
            aoc.util.FAILURE_EMOJI,
            aoc.util.FAILURE_EMOJI,
            aoc.util.FAILURE_EMOJI,
        )
        return False

    # Now look at trigrams, find any of the form ._.
    log.debug("Trigrams")
    for trigram in sliding_window(line, 3):
        log.debug(trigram)
        if trigram[0] == trigram[2]:
            log.debug("%s Looks good", aoc.util.SUCCESS_EMOJI)
            break
    else:
        log.debug(
            "%s%s%s NAUGHTY All trigrams are bad",
            aoc.util.FAILURE_EMOJI,
            aoc.util.FAILURE_EMOJI,
            aoc.util.FAILURE_EMOJI,
        )
        return False

    log.debug("NICE")
    return True


def part_one(lines: Iterable[str]) -> int:
    return sum(is_nice_part_one(line) for line in lines)


def part_two(lines: Iterable[str]) -> int:
    return sum(is_nice_part_two(line) for line in lines)
