import logging

import pyperclip

from aoc.util import Part, result_output_str, get_input_file_lines
from .util import YEAR, import_puzzle_module


log = logging.getLogger(__package__)


def run_puzzle_func(day: str | int, part: Part) -> bool:
    log.info(f"Part {part.value}")
    puzzle_module = import_puzzle_module(day)
    puzzle_func = puzzle_module.part_one if part == Part.ONE else puzzle_module.part_two

    raw_example = (
        puzzle_module.PART_ONE_EXAMPLE
        if part == Part.ONE
        else puzzle_module.PART_TWO_EXAMPLE
    )
    example = iter(raw_example.strip().split("\n")) if raw_example else None
    expected_example_result = (
        puzzle_module.PART_ONE_EXAMPLE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_EXAMPLE_RESULT
    )

    actual_example_result = puzzle_func(example) if example else None
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

    puzzle = get_input_file_lines(YEAR, day)
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
