#!/usr/bin/env python
"""
PART 1
Play games of Rock, Paper, Scissors according to a guide
Left column is opponent: A=Rock, B=Paper, C=Scissors
Right column is me: X=Rock, Y=Paper, Z=Scissors
Score each game:
1, 2, or 3 if I threw Rock, Paper, or Scissors; plus
0, 3, or 6 for Lose, Draw, or Win

PART 2
Play games of Rock, Paper, Scissors according to a guide
Left column is opponent: A=Rock, B=Paper, C=Scissors
Right column is the outcome I want: X=Lose, Y=Draw, Z=Win
Score each game:
1, 2, or 3 if I threw Rock, Paper, or Scissors; plus
0, 3, or 6 for Lose, Draw, or Win
"""
import logging
from collections.abc import Iterable
from typing import Literal

PART_ONE_EXAMPLE = """\
A Y
B X
C Z
"""
PART_ONE_EXAMPLE_RESULT = 15
PART_ONE_RESULT = 12645
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 12
PART_TWO_RESULT = 11756


ROCK = 1
PAPER = 2
SCISSORS = 3
type RPS = Literal[1, 2, 3]


def part_one(lines: Iterable[str]) -> int:
    def parse_line_and_score(line: str) -> int:
        them_str, me_str = line.split(maxsplit=2)
        # A=1, B=2, C=3
        them = ord(them_str) - ord("A") + 1
        # X=1, Y=2, Z=3
        me = ord(me_str) - ord("X") + 1

        # Win if I'm greater than them mod 3
        outcome = (me - them) % 3
        # Map outcomes from {0, 1, 2} to {0, 1, -1}
        outcome = -1 if outcome == 2 else outcome
        # Score outcomes -1, 0, 1 as 0, 3, 6
        outcome_score = (outcome + 1) * 3

        return me + outcome_score

    return sum(map(parse_line_and_score, lines))


def part_two(lines: Iterable[str]) -> int:
    def parse_line_and_score(line: str) -> int:
        them_str, outcome_str = line.split(maxsplit=2)
        # A=1, B=2, C=3
        them = ord(them_str) - ord("A") + 1
        # X=-1, Y=0, Z=1
        outcome = ord(outcome_str) - ord("Y")
        # I play what they play except adjusted to win, lose, or draw as instructed
        me = (them + outcome) % 3
        # Map {0, 1, 2} to {3, 1, 2}
        me_score = me if me else 3
        # Score outcomes -1, 0, 1 as 0, 3, 6
        outcome_score = (outcome + 1) * 3
        logging.debug(
            "%s %s -> %s + %s", them_str, outcome_str, me_score, outcome_score
        )
        return me_score + outcome_score

    return sum(map(parse_line_and_score, lines))
