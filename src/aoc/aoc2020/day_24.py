#!/usr/bin/env python
"""
PART 1
Identify tiles on a hex grid that get flipped

PART 2
Start with the setup from part 1, then follow the rule:
- A black tile with 0 or >2 black neighbors flips white
- A white tile with exactly 2 black neighbors flips to black
How many black tiles after 100 iterations?

(This is basically just like 2020 day 17.)
"""
from collections import Counter, defaultdict
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
sesenwnenenewseeswwswswwnenewsewsw
neeenesenwnwwswnenewnwwsewnenwseswesw
seswneswswsenwwnwse
nwnwneseeswswnenewneswwnewseswneseene
swweswneswnenwsewnwneneseenw
eesenwseswswnenwswnwnwsewwnwsene
sewnenenenesenwsewnenwwwse
wenwwweseeeweswwwnwwe
wsweesenenewnwwnwsenewsenwwsesesenwne
neeswseenwwswnwswswnw
nenwswwsewswnenenewsenwsenwnesesenew
enewnwewneswsewnwswenweswnenwsenwsw
sweneswneswneneenwnewenewwneswswnese
swwesenesewenwneswnwwneseswwne
enesenwswwswneneswsenwnewswseenwsese
wnwnesenesenenwwnenwsewesewsesesew
nenewswnwewswnenesenwnesewesw
eneswnwswnwsenenwnwnwwseeswneewsenese
neswnwewnwnwseenwseesewsenwsweewe
wseweeenwnesenwwwswnew
"""
PART_ONE_EXAMPLE_RESULT = 10
PART_ONE_RESULT = 488
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 2208
PART_TWO_RESULT = 4118


# See https://www.redblobgames.com/grids/hexagons/#coordinates-axial
type AxialHexVec = tuple[int, int]


def neighbors(tile: AxialHexVec) -> Iterable[AxialHexVec]:
    for offset in (1, -1):
        yield tile[0], tile[1] + offset
        yield tile[0] + offset, tile[1]
        yield tile[0] + offset, tile[1] - offset


def parse(line: str) -> AxialHexVec:
    hexvecdict = {"q": 0, "r": 0}
    lline = len(line)
    i = 0
    while i < lline:
        if line[i] in "ew":
            hexvecdict["q"] += 1 if line[i] == "e" else -1
            i -= 1
        elif line[i : i + 2] in {"nw", "se"}:
            hexvecdict["r"] += 1 if line[i + 1] == "e" else -1
        else:
            offset = 1 if line[i + 1] == "e" else -1
            hexvecdict["q"] += offset
            hexvecdict["r"] -= offset

        i += 2

    return hexvecdict["q"], hexvecdict["r"]


def find_black_tiles(lines: Iterable[str]) -> set[AxialHexVec]:
    visited = Counter(parse(line) for line in lines)
    return {tile for tile, times_visited in visited.items() if times_visited % 2}


def apply_rules(black_tiles: set[AxialHexVec]) -> set[AxialHexVec]:
    new_black_tiles = set()
    white_tiles_black_neighbors = defaultdict(int)
    for black_tile in black_tiles:
        black_tile_black_neighbors = 0
        for n in neighbors(black_tile):
            if n in black_tiles:
                black_tile_black_neighbors += 1
            else:
                white_tiles_black_neighbors[n] += 1
        if black_tile_black_neighbors == 1 or black_tile_black_neighbors == 2:
            new_black_tiles.add(black_tile)

    new_black_tiles.update(
        white_tile
        for white_tile, num_black_neighbors in white_tiles_black_neighbors.items()
        if num_black_neighbors == 2
    )
    return new_black_tiles


def part_one(lines: Iterable[str]) -> int:
    return len(find_black_tiles(lines))


def part_two(lines: Iterable[str]) -> int:
    black_tiles = find_black_tiles(lines)

    for d in range(100):
        black_tiles = apply_rules(black_tiles)
    return len(black_tiles)
