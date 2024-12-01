import datetime
from typing import Optional

from aoc.util import Part, import_year


def run_puzzle(datestamp: Optional[str], parts_arg: Optional[list[int]] = None) -> bool:
    date = (
        datetime.date.today()
        if not datestamp
        else datetime.date.fromisoformat(datestamp)
    )
    parts = [Part(part) for part in parts_arg] if parts_arg else None

    year_package = import_year(date.year)

    if parts_arg:
        return all(year_package.run_puzzle_func(date.day, part) for part in parts)

    # If they didn't pass an explicit parts arg...
    # - run part 1
    # - If part 1 returns None, stop and exit
    # - Otherwise return part 1 result AND part 2 result

    part1_result = year_package.run_puzzle_func(date.day, Part.ONE)
    if part1_result is None:
        # This means we found part 1's result and copied it to the clipboard
        return True
    return part1_result and year_package.run_puzzle_func(date.day, Part.TWO)
