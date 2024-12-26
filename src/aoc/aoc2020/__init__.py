from typing import Iterable, Optional

import aoc.util


def import_puzzle_module(day: str | int):
    return aoc.util.import_puzzle_module(__package__, day)


def get_input_file_lines(day: str | int) -> Iterable[str]:
    return aoc.util.get_input_file_lines(YEAR, day)


def run_puzzle_func(day: str | int, part: aoc.util.Part) -> Optional[bool]:
    return aoc.util.run_puzzle_func(import_puzzle_module, YEAR, day, part)


YEAR = 2020
