import datetime
from typing import Optional

from aoc.util import Part, import_year


def run_puzzle(datestamp: Optional[str], parts_arg: Optional[list[int]] = None) -> bool:
    date = (
        datetime.date.today()
        if not datestamp
        else datetime.date.fromisoformat(datestamp)
    )
    parts = [Part(part) for part in parts_arg] if parts_arg else [Part.ONE, Part.TWO]

    year_package = import_year(date.year)

    return all(year_package.run_puzzle_func(date.day, part) for part in parts)
