from collections.abc import Callable, Iterable

import pytest

from aoc.util import Part, PuzzleModule


def template_test_puzzle_solution(
    get_input_file_lines: Callable[[str | int], Iterable[str]],
    import_puzzle_module: Callable[[str | int], PuzzleModule],
    day: int,
    part: Part,
):
    input_file_lines = get_input_file_lines(day)
    puzzle_module = import_puzzle_module(day)
    puzzle_func = puzzle_module.part_one if part == Part.ONE else puzzle_module.part_two

    raw_example = (
        puzzle_module.PART_ONE_EXAMPLE
        if part == Part.ONE
        else puzzle_module.PART_TWO_EXAMPLE
    )
    raw_example = raw_example.rstrip("\n")
    example = iter(raw_example.split("\n"))

    expected_example_result = (
        puzzle_module.PART_ONE_EXAMPLE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_EXAMPLE_RESULT
    )
    if expected_example_result:
        actual_example_result = puzzle_func(example)
        assert expected_example_result == actual_example_result

    expected_puzzle_result = (
        puzzle_module.PART_ONE_RESULT
        if part == Part.ONE
        else puzzle_module.PART_TWO_RESULT
    )

    if expected_puzzle_result is not None:
        actual_puzzle_result = puzzle_func(iter(input_file_lines))
        assert expected_puzzle_result == actual_puzzle_result


def generate_pytest_generate_tests(marks: dict[tuple[int, Part], str], days: int):
    def pytest_generate_tests(metafunc):
        # Find puzzle modules
        # Parametrize test func
        metafunc.parametrize(
            "day,part",
            [
                pytest.param(
                    day + 1,
                    part,
                    **(
                        {"marks": mark}
                        if (mark := marks.get((day + 1, part))) is not None
                        else {}
                    ),
                )
                for day in range(days)
                for part in Part
            ],
        )

    return pytest_generate_tests
