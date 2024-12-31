import pytest

from aoc.util import Part
from aoc.aoc2022 import test_puzzle_solution  # noqa: F401
from aoc.testing.util import generate_pytest_generate_tests


marks = {
    (15, Part.TWO): pytest.mark.skip("Takes too long"),
    (16, Part.TWO): pytest.mark.skip("Takes too long"),
    (17, Part.TWO): pytest.mark.xfail,
}

pytest_generate_tests = generate_pytest_generate_tests(marks, 18)
