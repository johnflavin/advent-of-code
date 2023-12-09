#!/usr/bin/env python
"""

PART 1
Add the IDs of games that would have been possible if the bag contained only
12 red cubes, 13 green cubes, and 14 blue cubes

PART 2
Find the product of the minimum number of cubes that would
have needed to be there for each game to be possible
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass


PART_ONE_EXAMPLE = """\
Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
"""
PART_ONE_EXAMPLE_RESULT = 8
PART_ONE_RESULT = 1734
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 2286
PART_TWO_RESULT = 70387


GAME = re.compile(r"^Game (\d+)")
RED = re.compile(r".*?(\d+) red.*")
BLUE = re.compile(r".*?(\d+) blue.*")
GREEN = re.compile(r".*?(\d+) green.*")


@dataclass
class CubeSet:
    red: int = 0
    blue: int = 0
    green: int = 0

    def __init__(
        self, cube_set: str = None, red: int = 0, blue: int = 0, green: int = 0
    ):
        if red:
            self.red = red
        elif red_m := RED.match(cube_set):
            self.red = int(red_m.group(1))
        if blue:
            self.blue = blue
        elif blue_m := BLUE.match(cube_set):
            self.blue = int(blue_m.group(1))
        if green:
            self.green = green
        elif green_m := GREEN.match(cube_set):
            self.green = int(green_m.group(1))

    def is_possible(self, limits: "CubeSet"):
        return (
            self.red <= limits.red
            and self.blue <= limits.blue
            and self.green <= limits.green
        )

    @property
    def power(self):
        return self.red * self.blue * self.green


@dataclass
class Game:
    game_id: int
    cube_sets: list[CubeSet]

    def __init__(self, line: str):
        prefix, cube_sets = line.split(": ")
        if match := GAME.match(prefix):
            self.game_id = int(match.group(1))
        else:
            raise Exception(f"No game id found for line {line}")
        self.cube_sets = [
            CubeSet(cube_set) for cube_set in cube_sets.split("; ") if cube_set
        ]

    def is_possible(self, limits: CubeSet):
        return all(cube_set.is_possible(limits) for cube_set in self.cube_sets)

    @property
    def minimum_possible(self) -> CubeSet:
        maxes = [0, 0, 0]
        for cube_set in self.cube_sets:
            if cube_set.red > maxes[0]:
                maxes[0] = cube_set.red
            if cube_set.blue > maxes[1]:
                maxes[1] = cube_set.blue
            if cube_set.green > maxes[2]:
                maxes[2] = cube_set.green
        return CubeSet(red=maxes[0], blue=maxes[1], green=maxes[2])


def game_id_if_possible(line: str, limits: tuple[int, int, int]) -> int:
    for pattern, limit in zip((RED, BLUE, GREEN), limits):
        for match in pattern.finditer(line):
            if int(match.group(1)) > limit:
                print("Impossible", match.group(0), ">", limit)
                return 0
    if game_match := GAME.match(line):
        print(game_match.group(0), "Possible")
        return int(game_match.group(1))
    return 0


def part_one(lines: Iterable[str]) -> int:
    limits = CubeSet(red=12, blue=14, green=13)
    return sum(
        game.game_id
        for line in lines
        if line and (game := Game(line)).is_possible(limits)
    )


def part_two(lines: Iterable[str]) -> int:
    return sum(Game(line).minimum_possible.power for line in lines if line)
