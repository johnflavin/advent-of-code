#!/usr/bin/env python
"""

PART 1
Find the sum of all numbers adjacent to a symbol (not ".")
Adjacency is linear and diagonal, numbers are the whole digit strings

PART 2
The * symbols that are adjacent to exactly two numbers are "gears".
The product of their two numbers is the "gear ratio".
Find the sum of all the gear ratios.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from math import prod


PART_ONE_EXAMPLE = """\
467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..
"""
PART_ONE_EXAMPLE_RESULT = 4361
PART_ONE_RESULT = 527364
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 467835
PART_TWO_RESULT = 79026871


@dataclass
class Nothing:
    pass


@dataclass
class Digit:
    digits: list[str] = field(default_factory=list)
    already_included_in_total: bool = False
    already_included_in_symbol_gear_ratio: list["Symbol"] = field(default_factory=list)

    @property
    def digit(self) -> int:
        return int("".join(self.digits))


@dataclass
class Symbol:
    symbol: str
    adjacent_digits: list[Digit] = field(default_factory=list)

    @property
    def gear_ratio(self):
        if self.symbol == "*" and len(self.adjacent_digits) == 2:
            return prod(digit.digit for digit in self.adjacent_digits)
        else:
            return 0


Line = list[Nothing | Digit | Symbol]
CheckLine = list[tuple[Symbol, int]]


def make_empty_line(length: int) -> Line:
    return [Nothing()] * length


def total_line(line: Line, indexes_to_check: CheckLine) -> int:
    total = 0
    for adjacent_symbol, checking_idx in indexes_to_check:
        checking = line[checking_idx]
        if type(checking) is Digit:
            if not checking.already_included_in_total:
                total += checking.digit
                checking.already_included_in_total = True
    return total


def mark_digit_symbol_adjacencies(line: Line, indexes_to_check: CheckLine):
    for adjacent_symbol, checking_idx in indexes_to_check:
        checking = line[checking_idx]
        if type(checking) is Digit:
            if not any(
                symbol is adjacent_symbol
                for symbol in checking.already_included_in_symbol_gear_ratio
            ):
                adjacent_symbol.adjacent_digits.append(checking)
                checking.already_included_in_symbol_gear_ratio.append(adjacent_symbol)


def check_line_gears(line: Line) -> int:
    return sum(checking.gear_ratio for checking in line if type(checking) is Symbol)


class ParserRunner:
    line_length: int
    total: int
    gear_ratio: int
    indexes_to_check_prev_line: CheckLine
    indexes_to_check_this_line: CheckLine
    indexes_to_check_next_line: CheckLine
    previous_line: Line
    current_line: Line

    def __init__(self, lines: Iterable[str]):
        self.total = 0
        self.gear_ratio = 0
        self.indexes_to_check_prev_line = []
        self.indexes_to_check_this_line = []
        self.indexes_to_check_next_line = []

        lines_iter = iter(lines)
        first_line = next(lines_iter)
        self.line_length = len(first_line)
        self.previous_line = make_empty_line(self.line_length)
        self.run_line(first_line)

        for line in lines:
            self.run_line(line)

        # last line
        self.run_line("")

    def parse_line(self, line: str):
        parsed_line = make_empty_line(self.line_length)
        current_digit = None
        for idx, ch in enumerate(line):
            if ch in "1234567890":
                # We have a digit
                # is this a new digit or part of an existing digit?
                current_digit = current_digit if current_digit is not None else Digit()
                current_digit.digits.append(ch)
                parsed_line[idx] = current_digit
            elif ch != ".":
                current_symbol = Symbol(ch)
                parsed_line[idx] = current_symbol
                current_digit = None
                self.indexes_to_check_prev_line.append((current_symbol, idx))
                self.indexes_to_check_next_line.append((current_symbol, idx))
                if idx < self.line_length - 1:
                    self.indexes_to_check_prev_line.append((current_symbol, idx + 1))
                    self.indexes_to_check_this_line.append((current_symbol, idx + 1))
                    self.indexes_to_check_next_line.append((current_symbol, idx + 1))
                if idx > 0:
                    self.indexes_to_check_prev_line.append((current_symbol, idx - 1))
                    self.indexes_to_check_this_line.append((current_symbol, idx - 1))
                    self.indexes_to_check_next_line.append((current_symbol, idx - 1))
            else:
                current_digit = None

        self.current_line = parsed_line

    def set_up_for_next_line(self):
        self.previous_line = self.current_line
        self.indexes_to_check_prev_line = self.indexes_to_check_this_line
        self.indexes_to_check_this_line = self.indexes_to_check_next_line
        self.indexes_to_check_next_line = []

    def run_line(self, line: str):
        self.parse_line(line)

        self.total += total_line(self.previous_line, self.indexes_to_check_prev_line)
        mark_digit_symbol_adjacencies(
            self.previous_line, self.indexes_to_check_prev_line
        )
        mark_digit_symbol_adjacencies(
            self.current_line, self.indexes_to_check_this_line
        )
        self.gear_ratio += check_line_gears(self.previous_line)

        self.set_up_for_next_line()


def part_one(lines: Iterable[str]) -> int:
    # Scan board for symbols. store adjacent indices in a set
    # turn indices to search into indices of digits in a set
    # turn indices of digits into numbers
    # sum
    return ParserRunner(lines).total


def part_two(lines: Iterable[str]) -> int:
    return ParserRunner(lines).gear_ratio
