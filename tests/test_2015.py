from aoc.aoc2015 import test_puzzle_solution  # noqa: F401
from aoc.testing.util import generate_pytest_generate_tests


marks = {}

pytest_generate_tests = generate_pytest_generate_tests(marks, 6)
