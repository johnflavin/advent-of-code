import importlib
import logging
import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Protocol, Self, cast

import pyperclip
import requests
import requests.utils

RESOURCES = Path(__package__).parent / "resources"
INPUT_RESOURCES = RESOURCES / "inputs"
SESSION_COOKIE_FILE = RESOURCES / "session.txt"

SUCCESS_EMOJI = "\u2705"
FAILURE_EMOJI = "\u274C"


log = logging.getLogger(__name__)


def result_output_str(expected: int | str | None, actual: int | str | None) -> str:
    correct = expected == actual
    eq = "=" if correct else "≠"
    emoji = SUCCESS_EMOJI if correct else FAILURE_EMOJI
    return f"actual {actual} {eq} expected {expected} {emoji}"


class Part(Enum):
    ONE = 1
    TWO = 2


class YearPackage(Protocol):
    def run_puzzle_func(self, day: str | int, part: Part) -> bool: ...


class PuzzleModule(Protocol):
    PART_ONE_EXAMPLE: str
    PART_TWO_EXAMPLE: str
    PART_ONE_EXAMPLE_RESULT: int | str
    PART_TWO_EXAMPLE_RESULT: int | str
    PART_ONE_RESULT: int | str | None
    PART_TWO_RESULT: int | str | None

    def part_one(self, lines: Iterable[str]) -> int | str: ...

    def part_two(self, lines: Iterable[str]) -> int | str: ...


def import_puzzle_module(year_package: str, day: str | int) -> PuzzleModule:
    """Find the main function for the puzzle"""
    module = importlib.import_module(f".day_{day:02}", package=year_package)
    return cast(PuzzleModule, module)


def run_puzzle_func(
    import_puzzle_module_func: Callable[[str], PuzzleModule],
    year: str | int,
    day: str | int,
    part: Part,
) -> Optional[bool]:
    log.info(f"Part {part.value}")
    puzzle_module = import_puzzle_module_func(day)
    puzzle_func = puzzle_module.part_one if part == Part.ONE else puzzle_module.part_two

    raw_example = (
        puzzle_module.PART_ONE_EXAMPLE
        if part == Part.ONE
        else puzzle_module.PART_TWO_EXAMPLE
    )
    example = iter(raw_example.rstrip("\n").split("\n")) if raw_example else None
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

    puzzle = get_input_file_lines(year, day)
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
        return None

    log.info(
        "Puzzle: %s", result_output_str(expected_puzzle_result, actual_puzzle_result)
    )
    return expected_puzzle_result == actual_puzzle_result


def import_year(year: str | int) -> YearPackage:
    """Find package for the year's puzzle modules"""
    module = importlib.import_module(f"aoc.aoc{year}", package=__package__)
    return cast(YearPackage, module)


def download_puzzle_data(year: str | int, day: str | int) -> bytes:
    url = f"https://adventofcode.com/{year}/day/{day}/input"
    cookie = read_session_cookie()

    s = requests.Session()
    requests.utils.add_dict_to_cookiejar(s.cookies, {"session": cookie})
    r = s.get(url)
    r.raise_for_status()
    return r.content


def read_session_cookie() -> str:
    with open(SESSION_COOKIE_FILE, "r") as f:
        return f.read().strip()


def find_input_file(year: str | int, day: str | int) -> Path:
    return INPUT_RESOURCES / f"{year}-12-{day:02}.txt"


def get_input_file_data_and_write_file(
    year: str | int, day: str | int, input_file: Path
):
    try:
        with open(input_file, "wb") as f:
            f.write(download_puzzle_data(year, day))
    except requests.RequestException as e:
        os.remove(input_file)
        print(e.response.status_code, e.response.text)
        raise SystemExit(f"Could not load data for {year}-12-{day:02}")


def get_input_file_lines(year: str | int, day: str | int) -> Iterable[str]:
    input_file = find_input_file(year, day)
    if not input_file.exists():
        get_input_file_data_and_write_file(year, day, input_file)

    def inner():
        with input_file.open("r") as f:
            yield from f

    return map(lambda line: line.rstrip(), inner())


type Coord = tuple[int, int]


OFFSETS = (
    (-1, 0),
    (0, -1),
    (1, 0),
    (0, 1),
)


def add(a: Coord, b: Coord) -> Coord:
    return a[0] + b[0], a[1] + b[1]


def sub(a: Coord, b: Coord) -> Coord:
    return a[0] - b[0], a[1] - b[1]


def neighbors(pt: Coord) -> Iterable[Coord]:
    for delta in OFFSETS:
        yield add(pt, delta)


def revsub(one: int, two: int) -> int:
    return two - one


@dataclass(frozen=True, repr=False)
class Range:
    lower: int
    upper: int

    def is_empty(self) -> bool:
        return self.lower > self.upper

    def overlaps(self: Self, other: Self) -> bool:
        return (
            not other.is_empty()
            and not self.is_empty()
            and self.lower <= other.upper
            and other.lower <= self.upper
        )

    def __iter__(self):
        return iter(range(self.lower, self.upper + 1))

    def __and__(self: Self, other: Self) -> Self:
        """Overlap between self and other"""
        if not self.overlaps(other):
            return EmptyRange
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        return Range(lower, upper)

    def __sub__(self: Self, other: Self) -> list[Self]:
        """Non-overlapping parts of self and other
        (lower and upper). Either or both may be EmptyRange."""
        # Non-overlapping cases
        if other.upper < self.lower or self.upper < other.lower:
            # Self is above or below
            return [self]

        # Some overlap exists
        shards = []
        if self.lower < other.lower:
            shards.append(Range(self.lower, other.lower - 1))
        if self.upper > other.upper:
            shards.append(Range(other.upper + 1, self.upper))

        return shards

    def __contains__(self: Self, other: Self | int) -> bool:
        """Other range is completely contained within self"""
        if isinstance(other, Range):
            return self.lower <= other.lower and self.upper >= other.upper
        else:
            return self.lower <= other <= self.upper

    def __lt__(self: Self, other: Self):
        return (self.lower, self.upper) < (other.lower, other.upper)

    def __le__(self: Self, other: Self):
        return (self.lower, self.upper) <= (other.lower, other.upper)

    def __gt__(self: Self, other: Self):
        return (self.lower, self.upper) > (other.lower, other.upper)

    def __ge__(self: Self, other: Self):
        return (self.lower, self.upper) >= (other.lower, other.upper)

    def __eq__(self: Self, other: Self):
        return (self.lower, self.upper) == (other.lower, other.upper)

    def __ne__(self: Self, other: Self):
        return (self.lower, self.upper) != (other.lower, other.upper)

    def __len__(self) -> int:
        return self.upper - self.lower + 1

    def __repr__(self):
        return f"{self.lower},{self.upper}"


EmptyRange = Range(0, -1)
