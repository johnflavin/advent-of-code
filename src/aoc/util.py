import importlib
import os
from collections.abc import Iterable
from enum import Enum
from pathlib import Path
from typing import Protocol, cast

import requests
import requests.utils


RESOURCES = Path(__package__).parent / "resources"
INPUT_RESOURCES = RESOURCES / "inputs"
SESSION_COOKIE_FILE = RESOURCES / "session.txt"

SUCCESS_EMOJI = "\u2705"
FAILURE_EMOJI = "\u274C"


def result_output_str(expected: int | str | None, actual: int | str | None) -> str:
    correct = expected == actual
    eq = "=" if correct else "≠"
    emoji = SUCCESS_EMOJI if correct else FAILURE_EMOJI
    return f"actual {actual} {eq} expected {expected} {emoji}"


class Part(Enum):
    ONE = 1
    TWO = 2


# class PuzzleModule(Protocol):
#     # PART_ONE_EXAMPLE: str
#     # PART_TWO_EXAMPLE: str
#     # PART_ONE_EXAMPLE_RESULT: int | str
#     # PART_TWO_EXAMPLE_RESULT: int | str
#     # PART_ONE_RESULT: int | str | None
#     # PART_TWO_RESULT: int | str | None
#
#     def part_one(self, lines: Iterable[str]) -> int | str: ...
#
#     def part_two(self, lines: Iterable[str]) -> int | str: ...


class YearPackage(Protocol):
    def run_puzzle_func(self, day: str | int, part: Part) -> bool: ...


def import_year(year: str | int) -> YearPackage:
    """Find package for the year's puzzle modules"""
    module = importlib.import_module(f"aoc.aoc{year}", package=__package__)
    return cast(YearPackage, module)


class Part(Enum):
    ONE = 1
    TWO = 2


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

    return map(lambda line: line.strip(), inner())
