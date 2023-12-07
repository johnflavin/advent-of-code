import importlib
import importlib.resources
from enum import Enum
from os import remove
from pathlib import Path
from typing import Iterable, Protocol, cast

import requests
from requests.utils import add_dict_to_cookiejar


RESOURCES = Path(__package__).parent / "resources"
INPUT_RESOURCES = RESOURCES / "inputs"
SESSION_COOKIE_FILE = RESOURCES / "session.txt"

YEAR = 2023


class PuzzleModule(Protocol):
    PART_ONE_EXAMPLE: str
    PART_TWO_EXAMPLE: str
    PART_ONE_EXAMPLE_RESULT: int | str
    PART_TWO_EXAMPLE_RESULT: int | str
    PART_ONE_RESULT: int | str | None
    PART_TWO_RESULT: int | str | None

    def part_one(self, lines: Iterable[str]) -> int | str:
        ...

    def part_two(self, lines: Iterable[str]) -> int | str:
        ...


class Part(Enum):
    ONE = 1
    TWO = 2


def import_puzzle_module(day: str | int) -> PuzzleModule:
    """Find the main function for the puzzle"""
    module = importlib.import_module(f".day_{day:02}", package=__package__)
    return cast(PuzzleModule, module)


def download_puzzle_data(day: str | int) -> bytes:
    url = f"https://adventofcode.com/{YEAR}/day/{day}/input"
    cookie = read_session_cookie()

    s = requests.Session()
    add_dict_to_cookiejar(s.cookies, {"session": cookie})
    r = s.get(url)
    r.raise_for_status()
    return r.content


def read_session_cookie() -> str:
    with open(SESSION_COOKIE_FILE, "r") as f:
        return f.read().strip()


def find_input_file(day: str | int) -> Path:
    return INPUT_RESOURCES / f"{YEAR}-12-{day:02}.txt"


def get_input_file_data_and_write_file(day: str | int, input_file: Path):
    try:
        with open(input_file, "wb") as f:
            f.write(download_puzzle_data(day))
    except requests.RequestException as e:
        remove(input_file)
        print(e.response.status_code, e.response.text)
        raise SystemExit(f"Could not load data for {YEAR}-12-{day:02}")


def get_input_file_lines(day: str | int) -> Iterable[str]:
    input_file = find_input_file(day)
    if not input_file.exists():
        get_input_file_data_and_write_file(day, input_file)

    def inner():
        with input_file.open("r") as f:
            yield from f

    return map(lambda line: line.strip(), inner())
