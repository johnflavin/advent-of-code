#!/usr/bin/env python
"""
PART 1
Follow some rules and move values around, read off result.

PART 2
We actually have way more values than before, fill in values
up to 1 million.
And we need to do 10 million moves, not just 100.
Multiply the two values clockwise of 1.
"""
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
389125467
"""
PART_ONE_EXAMPLE_RESULT = "67384529"
PART_ONE_RESULT = "74698532"
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 149245887792
PART_TWO_RESULT = 286194102744

# log = logging.getLogger(__name__)
# is_debug = log.isEnabledFor(logging.DEBUG)


def do_moves_but_fast_this_time(given_nums: list[int], moves: int) -> dict[int, int]:
    max_val = max(given_nums)

    # Each num points to the next num
    num_pointers = dict(zip(given_nums, given_nums[1:] + [given_nums[0]]))
    active = given_nums[0]

    for _ in range(moves):
        # if is_debug:
        #     log.debug("-- move %d --", m + 1)
        #     the_rest = []
        #     next_num = active
        #     while (next_num := num_pointers[next_num]) != active:
        #         the_rest.append(next_num)
        #     log.debug("cups: (%d) %s", active, " ".join(map(str, the_rest)))

        # "Pick up" three next to active
        hold = [num_pointers[active]]
        hold.append(num_pointers[hold[-1]])
        hold.append(num_pointers[hold[-1]])
        # if is_debug:
        #     log.debug("pick up: %s", " ".join(map(str, hold)))

        # Bridge the gap we made by picking these up
        num_pointers[active] = num_pointers[hold[-1]]

        # Find dest number
        dest = (active - 1) % max_val
        if dest == 0:
            dest = max_val
        while dest in hold:
            dest = (dest - 1) % max_val
            if dest == 0:
                dest = max_val
        # log.debug("destination: %d", dest)

        # Re-insert held items
        num_pointers[hold[-1]] = num_pointers[dest]
        num_pointers[dest] = hold[0]

        # Move active to next in the chain
        active = num_pointers[active]

        # log.debug("")
    return num_pointers


def part_one(lines: Iterable[str]) -> str:
    given_nums = [int(c) for c in "".join(lines)]

    pointers = do_moves_but_fast_this_time(given_nums, 100)

    num = 1
    ordered = []
    for _ in range(len(pointers) - 1):
        next_num = pointers[num]
        ordered.append(next_num)
        num = next_num

    return "".join(map(str, ordered))


def part_two(lines: Iterable[str]) -> int:
    given_nums = [int(c) for c in "".join(lines)]
    all_nums = given_nums + list(range(9 + 1, 1_000_001))
    pointers = do_moves_but_fast_this_time(all_nums, 10_000_000)

    num1 = pointers[1]
    num2 = pointers[num1]
    return num1 * num2
