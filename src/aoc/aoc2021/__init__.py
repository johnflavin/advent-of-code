import importlib
import logging

import pyperclip

from typing import Iterable, Optional, Protocol, cast

import aoc.util
from aoc.util import Part, result_output_str


log = logging.getLogger(__package__)


class PuzzleModule(Protocol):
    EXAMPLE: str
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


def run_puzzle_func(day: str | int, part: Part) -> bool:
    puzzle_module = import_puzzle_module(day)
    puzzle_func = puzzle_module.part_one if part == Part.ONE else puzzle_module.part_two

    example = iter(puzzle_module.EXAMPLE.rstrip("\n").split("\n"))
    expected_example_result = (
        puzzle_module.PART_ONE_EXAMPLE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_EXAMPLE_RESULT
    )

    actual_example_result = puzzle_func(example)
    example_is_correct = (
        actual_example_result == expected_example_result
        if actual_example_result is not None
        else True
    )
    example_output = (
        result_output_str(expected_example_result, actual_example_result)
        if actual_example_result is not None
        else "None provided"
    )

    log.info("Example: %s", example_output)
    if not example_is_correct:
        return False

    puzzle = get_input_file_lines(day)
    actual_puzzle_result = puzzle_func(puzzle)
    expected_puzzle_result = (
        puzzle_module.PART_ONE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_RESULT
    )

    if expected_puzzle_result is None:
        if actual_puzzle_result is not None:
            pyperclip.copy(actual_puzzle_result)
            log.info("Puzzle result copied to clipboard: %s", actual_puzzle_result)
        return True

    log.info(
        "Puzzle: %s", result_output_str(expected_puzzle_result, actual_puzzle_result)
    )
    return expected_puzzle_result == actual_puzzle_result


YEAR = 2021
