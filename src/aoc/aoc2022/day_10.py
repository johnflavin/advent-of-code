#!/usr/bin/env python
"""
PART 1
Receive a sequence of "addx <number>" and "noop" instructions.
Start with number X = 1, cycle = 0.
- noop does cycle += 1, X += 0
- addx does cycle += 2, X += <num>
The "cycle number" is supposed to tick up at some rate, so it would
actually take all values, and X stays the same during cycles where it does
not change.
At each step the "signal strength" is cycle number * X at that cycle number.
Find sum of signal strength during the
20th, 60th, 100th, 140th, 180th, and 220th cycles

PART 2
"""
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
addx 15
addx -11
addx 6
addx -3
addx 5
addx -1
addx -8
addx 13
addx 4
noop
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx -35
addx 1
addx 24
addx -19
addx 1
addx 16
addx -11
noop
noop
addx 21
addx -15
noop
noop
addx -3
addx 9
addx 1
addx -3
addx 8
addx 1
addx 5
noop
noop
noop
noop
noop
addx -36
noop
addx 1
addx 7
noop
noop
noop
addx 2
addx 6
noop
noop
noop
noop
noop
addx 1
noop
noop
addx 7
addx 1
noop
addx -13
addx 13
addx 7
noop
addx 1
addx -33
noop
noop
noop
addx 2
noop
noop
noop
addx 8
noop
addx -1
addx 2
addx 1
noop
addx 17
addx -9
addx 1
addx 1
addx -3
addx 11
noop
noop
addx 1
noop
addx 1
noop
noop
addx -13
addx -19
addx 1
addx 3
addx 26
addx -30
addx 12
addx -1
addx 3
addx 1
noop
noop
noop
addx -9
addx 18
addx 1
addx 2
noop
noop
addx 9
noop
noop
noop
addx -1
addx 2
addx -37
addx 1
addx 3
noop
addx 15
addx -21
addx 22
addx -6
addx 1
noop
addx 2
addx 1
noop
addx -10
noop
noop
addx 20
addx 1
addx 2
addx 2
addx -6
addx -11
noop
noop
noop
"""
PART_ONE_EXAMPLE_RESULT = 13140
PART_ONE_RESULT = 14620
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = """
##..##..##..##..##..##..##..##..##..##..
###...###...###...###...###...###...###.
####....####....####....####....####....
#####.....#####.....#####.....#####.....
######......######......######......####
#######.......#######.......#######....."""
PART_TWO_RESULT = """
###....##.####.###..#..#.###..####.#..#.
#..#....#.#....#..#.#..#.#..#.#....#..#.
###.....#.###..#..#.####.#..#.###..#..#.
#..#....#.#....###..#..#.###..#....#..#.
#..#.#..#.#....#.#..#..#.#.#..#....#..#.
###...##..#....#..#.#..#.#..#.#.....##.."""  # Draws letters BJFRHRFU


log = logging.getLogger(__name__)


NOOP = "noop"


def perform_instruction(line: str, cycle: int, x: int) -> tuple[int, int]:
    log.debug("cycle=%d x=%d executing %s", cycle, x, line)
    if line == NOOP:
        return cycle + 1, x
    addx = int(line.split()[1])
    return cycle + 2, x + addx


def part_one(lines: Iterable[str]) -> int:
    def find_signal_strengths() -> Iterable[int]:
        cycles_to_watch_for = (20, 60, 100, 140, 180, 220)
        cycle_watch_idx = 0

        cycle = 0
        x = 1
        for line in lines:
            if not line:
                continue
            new_cycle, new_x = perform_instruction(line, cycle, x)
            if new_cycle >= cycles_to_watch_for[cycle_watch_idx]:
                # Passed a threshold, yield new signal strength
                yield cycles_to_watch_for[cycle_watch_idx] * x

                # Watch for next value
                cycle_watch_idx += 1
                if cycle_watch_idx >= len(cycles_to_watch_for):
                    # There isn't another value to watch for
                    return
            # Update values
            cycle, x = new_cycle, new_x

    return sum(find_signal_strengths())


def part_two(lines: Iterable[str]) -> str:
    lines = filter(lambda line: line, lines)

    def make_raster() -> Iterable[str]:
        cycle = 1

        x_cycle = 1
        x = 1
        for line in lines:
            next_x_cycle, next_x = perform_instruction(line, x_cycle, x)
            while cycle < next_x_cycle:
                r_pos = (cycle - 1) % 40
                if r_pos == 0:
                    # Reached the end of a row, make a new line
                    log.debug("new line")
                    yield "\n"

                draw = "#" if abs(r_pos - x) < 2 else "."
                log.debug(
                    "Draw %s cycle=%d x_cycle=%d next_x_cycle=%d r_pos=%d x=%d",
                    draw,
                    cycle,
                    x_cycle,
                    next_x_cycle,
                    r_pos,
                    x,
                )

                yield draw
                cycle += 1
            x_cycle = next_x_cycle
            x = next_x

    return "".join(make_raster())
