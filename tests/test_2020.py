import pytest

from aoc.util import Part
from aoc.aoc2020 import test_puzzle_solution  # noqa: F401
from aoc.testing.util import generate_pytest_generate_tests


marks = {
    (15, Part.TWO): pytest.mark.skip("Takes too long"),
}

pytest_generate_tests = generate_pytest_generate_tests(marks, 20)
