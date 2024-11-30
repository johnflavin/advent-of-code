import importlib
import importlib.resources
from typing import Iterable, Protocol, cast

import aoc.util


YEAR = 2023


class PuzzleModule(Protocol):
    PART_ONE_EXAMPLE: str
    PART_TWO_EXAMPLE: str
    PART_ONE_EXAMPLE_RESULT: int | str
    PART_TWO_EXAMPLE_RESULT: int | str
    PART_ONE_RESULT: int | str | None
    PART_TWO_RESULT: int | str | None

    def part_one(self, lines: Iterable[str]) -> int | str: ...

    def part_two(self, lines: Iterable[str]) -> int | str: ...


def import_puzzle_module(day: str | int) -> PuzzleModule:
    """Find the main function for the puzzle"""
    module = importlib.import_module(f".day_{day:02}", package=__package__)
    return cast(PuzzleModule, module)


def get_input_file_lines(day: str | int) -> Iterable[str]:
    return aoc.util.get_input_file_lines(YEAR, day)
