#!/usr/bin/env python
"""
PART 1
Given tiles, need to align them by matching borders.
Can flip and rotate.
Multiply ids of corner tiles.

PART 2
Given aligned tiles from part 1, remove borders and concat into one tile.
Find "sea monsters" based on a pattern.
Count how many # tiles are not part of a sea monster.
"""
import itertools
import logging
import math
from collections import deque
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
Tile 2311:
..##.#..#.
##..#.....
#...##..#.
####.#...#
##.##.###.
##...#.###
.#.#.#..##
..#....#..
###...#.#.
..###..###

Tile 1951:
#.##...##.
#.####...#
.....#..##
#...######
.##.#....#
.###.#####
###.##.##.
.###....#.
..#.#..#.#
#...##.#..

Tile 1171:
####...##.
#..##.#..#
##.#..#.#.
.###.####.
..###.####
.##....##.
.#...####.
#.##.####.
####..#...
.....##...

Tile 1427:
###.##.#..
.#..#.##..
.#.##.#..#
#.#.#.##.#
....#...##
...##..##.
...#.#####
.#.####.#.
..#..###.#
..##.#..#.

Tile 1489:
##.#.#....
..##...#..
.##..##...
..#...#...
#####...#.
#..#.#.#.#
...#.#.#..
##.#...##.
..##.##.##
###.##.#..

Tile 2473:
#....####.
#..#.##...
#.##..#...
######.#.#
.#...#.#.#
.#########
.###.#..#.
########.#
##...##.#.
..###.#.#.

Tile 2971:
..#.#....#
#...###...
#.#.###...
##.##..#..
.#####..##
.#..####.#
#..#.#..#.
..####.###
..#.#.###.
...#.#.#.#

Tile 2729:
...#.#.#.#
####.#....
..#.#.....
....#..#.#
.##..##.#.
.#.####...
####.#.#..
##.####...
##..#.##..
#.##...##.

Tile 3079:
#.#.#####.
.#..######
..#.......
######....
####.#..#.
.#...#.##.
#.#####.##
..#.###...
..#.......
..#.###...
"""
PART_ONE_EXAMPLE_RESULT = 20899048083289
PART_ONE_RESULT = 45443966642567
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 273
PART_TWO_RESULT = 1607

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


type Tile = tuple[str, ...]

MONSTER_DELTAS = {
    (0, 1),
    (1, 2),
    (4, 2),
    (5, 1),
    (6, 1),
    (7, 2),
    (10, 2),
    (11, 1),
    (12, 1),
    (13, 2),
    (16, 2),
    (17, 1),
    (18, 0),
    (18, 1),
    (19, 1),
}
LMD = len(MONSTER_DELTAS)


def parse(lines: Iterable[str]) -> list[tuple[int, Tile]]:
    lines = iter(lines)

    tiles = []
    tile_id = -1
    tile_lines = []
    for line in lines:
        if line == "":
            tiles.append((tile_id, tuple(tile_lines)))
            tile_id = -1
            tile_lines = []
        elif tile_id == -1:
            tile_id = int(line[5:-1])
        else:
            tile_lines.append(line)

    if tile_lines:
        tiles.append((tile_id, tuple(tile_lines)))

    return tiles


def rotate(tile: Tile) -> Tile:
    lt = len(tile)
    new_tile = [
        "".join(tile[row_idx][-col_idx - 1] for row_idx in range(lt))
        for col_idx in range(lt)
    ]
    return tuple(new_tile)


def find_neighbors(
    tiles: dict[int, Tile]
) -> tuple[dict[int, Tile], dict[int, dict[tuple[int, int], int]]]:

    def top(tile: Tile) -> str:
        return tile[0]

    def bottom(tile: Tile) -> str:
        return tile[-1]

    def right(tile: Tile) -> str:
        return "".join(t[-1] for t in tile)

    def left(tile: Tile) -> str:
        return "".join(t[0] for t in tile)

    def match(tile1: Tile, tile2: Tile) -> tuple[Tile, tuple[int, int]]:
        """Check tiles for match.
        Returns
            Tile: tile2 in matching orientation (or 0 if no match)
            int: which neighbor of tile1 is tile2? 0=right, 1=north, 2=left, 3=south
        """
        tile1_top = top(tile1)
        tile1_bottom = bottom(tile1)
        tile1_left = left(tile1)
        tile2_right = right(tile1)

        original_tile2 = tile2

        for f, tile2 in enumerate(
            (
                original_tile2,
                original_tile2[::-1],
                tuple(t[::-1] for t in original_tile2),
            )
        ):

            # Try four rotations (with 0 being no rotation)
            for r in range(4):
                if r != 0:
                    tile2 = rotate(tile2)
                # Check four neighbors
                if tile2_right == left(tile2):
                    return tile2, (1, 0)
                elif tile1_top == bottom(tile2):
                    return tile2, (0, -1)
                elif tile1_left == right(tile2):
                    return tile2, (-1, 0)
                elif tile1_bottom == top(tile2):
                    return tile2, (0, 1)
        return (), (0, 0)

    neighbors = {}
    rotated_tiles = {}
    tile_queue = deque([])
    while tile_queue or tiles:
        if not tile_queue:
            tile_queue.append(tiles.popitem())
        t1id, t1 = tile_queue.popleft()

        if t1id in rotated_tiles:
            continue
        rotated_tiles[t1id] = t1

        t1neighbors = neighbors.get(t1id, {})

        for t2id, t2 in itertools.chain(tiles.items(), rotated_tiles.items()):
            if t2id == t1id:
                continue

            t2neighbors = neighbors.get(t2id, {})
            if t1id in t2neighbors.values():
                # We already know t1 is a neighbor of t2
                continue

            rotated_t2, neighb_num = match(t1, t2)
            if neighb_num != (0, 0):
                t1neighbors[neighb_num] = t2id
                neighbors[t1id] = t1neighbors

                # Also mark the neighbor relationship in reverse
                t2neighbors[(-neighb_num[0], -neighb_num[1])] = t1id
                neighbors[t2id] = t2neighbors

                tile_queue.append((t2id, rotated_t2))

    return rotated_tiles, neighbors


def part_one(lines: Iterable[str]) -> int:
    tiles = dict(parse(lines))
    _, neighbors = find_neighbors(tiles)

    if is_debug:
        for tid, tneighb in neighbors.items():
            log.debug("Tile %d neighbors %s", tid, tneighb)

    return math.prod(tid for tid, tneighb in neighbors.items() if len(tneighb) == 2)


def part_two(lines: Iterable[str]) -> int:
    tiles = dict(parse(lines))
    rotated_tiles, neighbors = find_neighbors(tiles)

    # Find all the tile positions from the neighbor relationships
    # First, find the top-left tile
    tid = -1
    for tid, tneighbors in neighbors.items():
        if tneighbors.keys() == {(0, 1), (1, 0)}:
            break
    original_tile = []
    while tid != -1:
        row = []
        left = tid

        # Find all the neighbors to the right
        while tid != -1:
            # Make sure we trim the border off the tile before adding it
            row.append(tl[1:-1] for tl in rotated_tiles[tid][1:-1])
            # Move pointer to the right
            tid = neighbors[tid].get((1, 0), -1)

        # We're at the end of a row
        # concat all lines of tiles in the row
        original_tile.extend("".join(row_lines) for row_lines in zip(*row))

        # Continue with next leftmost tile down
        tid = neighbors[left].get((0, 1), -1)
    if is_debug:
        for otline in original_tile:
            log.debug(otline)

    # Now it's time to find the sea monsters
    max_y = len(original_tile) - 2
    max_x = len(original_tile) - 19
    sea_monster_top_lefts = set()
    num_sea_monsters = 0

    # Three flips: identity, top/bottom, and left/right
    for f, tile in enumerate(
        (original_tile, original_tile[::-1], tuple(t[::-1] for t in original_tile))
    ):
        # Four rotations: 0, pi/2, pi, 3pi/2
        for r in range(4):
            if r > 0:
                tile = rotate(tile)

            for top_y in range(max_y):
                for left_x in range(max_x):
                    if all(
                        tile[top_y + y][left_x + x] == "#" for x, y in MONSTER_DELTAS
                    ):
                        num_sea_monsters += 1
                        sea_monster_top_lefts.add((left_x, top_y))

            if num_sea_monsters:
                break
        if num_sea_monsters:
            break
    if not num_sea_monsters:
        return -1

    if is_debug:
        log.debug("flip %d rotation %d", f, r)
        log.debug("top left pts: %s", sea_monster_top_lefts)
        sea_monsters = {
            (left_x + x, top_y + y)
            for left_x, top_y in sea_monster_top_lefts
            for x, y in MONSTER_DELTAS
        }
        for y, line in enumerate(tile):
            log.debug(
                "".join(
                    "O" if (x, y) in sea_monsters else c for x, c in enumerate(line)
                )
            )

    return sum(c == "#" for line in tile for c in line) - LMD * num_sea_monsters
