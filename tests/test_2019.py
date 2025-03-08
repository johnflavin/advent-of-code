import pytest

from aoc.aoc2019 import test_puzzle_solution  # noqa: F401
from aoc.testing.util import generate_pytest_generate_tests
from aoc.util import Part

marks = {
    (15, Part.ONE): pytest.mark.skip("Takes too long"),
    (15, Part.TWO): pytest.mark.skip("Takes too long"),
}

pytest_generate_tests = generate_pytest_generate_tests(marks, 16)
