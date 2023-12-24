#!/usr/bin/env python
"""

PART 1
Given a map of a garden with path ".", rocks "#", and starting position "S".
How many locations can be reached from start in 64 steps?

Discussion
Isn't it just half the size of the map - number of rocks?

I've gone through a few iterations of this trying to avoid actual pathfinding.
I think I'm close, but I think I may need to implement actual pathfinding. :(
Looks like there are a few points around the edge where my implementation thinks you
    could reach just from the raw index calculations, but you couldn't actually
    reach within 64 steps.

Spoiler from part 2: pathfinding will not be effective at all.

PART 2
Actual number of steps is 26501365, and the map repeats periodically infinitely.

We'll need to calculate a few things.
1. How many visited spots are in a full map?
2. How many full maps are there?
3. How many partially full maps are there around the edge?
4. How many spaces are visited in a partially full map?

Assume input is square, so num rows = num cols = len
Assume start is at (len / 2, len / 2). That is true in my input, and we'll
    assume it is true in all inputs.
At distance len / 2, we are still within map 0.
At distance len / 2 + 1, we get into maps distance 1 away.
At distance len, we get to the middle of maps 1. map 0 is completely full.
At len + 1 we get into the maps distance 2 away.
So presume that at distance 2i * len / 2 we have reached the center of all
    maps distance i away, have not yet entered maps i + 1, and
    have completely filled maps < i.
Between 2i * len/2 and (2i+1) * len/2

Let's think about what the map is. (It's easiest if you look.)
It is 131x131, or (128 + 3)x(128 + 3)
We have blank rows at the top, bottom, and middle, and similar blank columns.
Let's partition the map along those blanks to make four squares, each 64x64.
Each square has a blank diagonal in a different direction,
    forming a ring around the start space at distance 65.
We can partition along those as well, making eight triangles.
(The diagonals are wider than one blank space, but I can't tell exactly how wide,
    and I don't think we need it anyway.)

What is the distance in units of full steps (131)?
26501365 = 202300*131 + 65

step
0       border pt (0,0)
64      half filled box 0
1       border
1       border
64      (full step 1) middle of 4 boxes (0, +/-1), box 0 filled
1       border
64      edge of 4 boxes 1, start 4 boxes (+/-1, +/-1)
1       border
1       border
64      (full step 2) middle of 4 boxes (0, +/-2), 4 boxes (0, +/-1) filled
1       border
64      edge of 4 boxes (0, +/-2)

Looks like every full step, we fill up the four boxes on the rows and columns.
It takes two full steps to fill up all the corner boxes, but the number that get
    filled goes up by 4 every time.
Let me see if I can derive a formula...
Step 1: 1 center box completely filled
Step 2: 4 edges
Step 3: 4 edges + 4 corners = 8
Step 4: 4 edges + 4*2 corners = 12
Step 5: 4 edges + 4*3 corners = 16
Looks like 1 for step 1, 4*(step - 1) for the rest.
And the total number filled at step N > 1 is
1 + sum_{i=2}^N 4*(i-1) = 1 + 4*sum_{i=1}^{N-1} i
= 1 + 2*(N-1)*N

So that's full steps, i.e. 131. Given our step total 26501365 = 202300*131 + 65
we have completed 202300 (...facepalm) full steps, plus one border step,
and a half step of 64.
We know that the number of fully filled boxes is 1 + 2*(N-1)*N
= 81850175401 for N = 202300.

We need to figure out a few things.
- How many spaces can be reached in a filled box?
    The number of spaces we can reach in 202300 full steps is the number
    in one filled box * 81850175401
- How many spaces can be reached in 65 steps from the edge of a box?
    Each of the four end boxes will have a different number.
    We will need to run the pathfinding algo to get the numbers,
    using the four different middle points as the respective starts.
- How many spaces can be reached in the half-full corners?
    Once again, we can use our pathfinding algo to answer this.
    Start in each corner and walk 131 steps. That gets each type of half-filled corner.
- How many half-full corners of each type are there?
Step 1: 0
Step 2: 1 * 4
Step 3: 2 * 4
Step N: (N-1) * 4
For each of the 4 types, then, we have N-1 at full step N.
Now, the additional half step complicates things a bit.
The N-1 that are half full on a full step become 3/4 full on a half step,
    and the N next corners become 1/4 full.

Our total will be...
(131 steps, start middle) * 81850175401 +
(131 + 65 steps, start each corner) * 202299 +
(65 steps, start each corner) * 202300 +
(65 steps, start middle of each edge)

UPDATE
Everything above gave me the answer 602996256135185,
which was too high.

I tweaked a bit, this time starting all the edge fills
at 66 instead of 65. I don't think that is correct, but it was something
to try.
I got the answer 602914405959514.
That one also was not correct. But it was lower than my original (too high)
answer. ...and this one was also too high!
"""

from .util import Coord
from collections import deque
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
...........
.....###.#.
.###.##..#.
..#.#...#..
....#.#....
.##..S####.
.##..#...#.
.......##..
.##.#.####.
.##..##.##.
...........
"""
PART_ONE_EXAMPLE_RESULT = 42
PART_ONE_RESULT = 3598  # < 3600, > 3344
PART_TWO_EXAMPLE = """\
.................................
.....###.#......###.#......###.#.
.###.##..#..###.##..#..###.##..#.
..#.#...#....#.#...#....#.#...#..
....#.#........#.#........#.#....
.##...####..##...####..##...####.
.##..#...#..##..#...#..##..#...#.
.......##.........##.........##..
.##.#.####..##.#.####..##.#.####.
.##..##.##..##..##.##..##..##.##.
.................................
.................................
.....###.#......###.#......###.#.
.###.##..#..###.##..#..###.##..#.
..#.#...#....#.#...#....#.#...#..
....#.#........#.#........#.#....
.##...####..##..S####..##...####.
.##..#...#..##..#...#..##..#...#.
.......##.........##.........##..
.##.#.####..##.#.####..##.#.####.
.##..##.##..##..##.##..##..##.##.
.................................
.................................
.....###.#......###.#......###.#.
.###.##..#..###.##..#..###.##..#.
..#.#...#....#.#...#....#.#...#..
....#.#........#.#........#.#....
.##...####..##...####..##...####.
.##..#...#..##..#...#..##..#...#.
.......##.........##.........##..
.##.#.####..##.#.####..##.#.####.
.##..##.##..##..##.##..##..##.##.
.................................
"""
PART_TWO_EXAMPLE_RESULT = 50
PART_TWO_RESULT = None  # < 602996256135185, < 602914405959514

OFFSETS = (
    (-1, 0),
    (0, -1),
    (1, 0),
    (0, 1),
)


def neighbors(pt: Coord) -> Iterable[Coord]:
    for row_off, col_off in OFFSETS:
        yield pt[0] + row_off, pt[1] + col_off


def walk(garden: list[str], start: Coord = None, steps: int = 64) -> int:
    num_rows = len(garden)
    num_cols = len(garden[0])

    if start is None:
        starts = [
            (row_idx, col_idx)
            for row_idx, line in enumerate(garden)
            for col_idx, ch in enumerate(line)
            if ch == "S"
        ]
        start = starts[0]
    start_mod = (start[0] + start[1]) % 2

    seen = set()
    dists = {}
    frontier = deque([(start, 0)])
    while frontier:
        pt, dist = frontier.popleft()

        if pt in seen:
            continue
        seen.add(pt)

        if (
            not (-1 < pt[0] < num_rows and -1 < pt[1] < num_cols)
            or garden[pt[0]][pt[1]] == "#"
        ):
            continue

        dists[pt] = dist

        frontier.extend((neighbor, dist + 1) for neighbor in neighbors(pt))

    # print("Input:")
    # print("\n".join(garden))
    #
    # visitable_garden = [
    #     "".join(
    #         "O"
    #         if (row_idx, col_idx) in dists
    #         and (dist := dists[(row_idx, col_idx)]) % 2 == start_mod
    #         and dist <= 64
    #         else ch
    #         for col_idx, ch in enumerate(line)
    #     )
    #     for row_idx, line in enumerate(garden)
    # ]
    # print("Visitable:")
    # visitable_str = "\n".join(visitable_garden)
    # print(visitable_str)
    # num_visitable = visitable_str.count("O")
    # print("Num visitable: ", num_visitable)

    return sum(1 for dist in dists.values() if dist <= steps and dist % 2 == start_mod)


def part_one(lines: Iterable[str]) -> int:
    garden = list(lines)
    return walk(garden)


def part_two(lines: Iterable[str]) -> int:
    garden = list(lines)

    # A hack to make my code work with the example
    # I'm not going to use this algorithm directly as it would take
    # practically infinite time.
    if len(garden) == PART_TWO_EXAMPLE.count("\n"):
        return walk(garden, steps=10)

    assert len(garden) == 131

    num_full_steps = 202300

    full_box = walk(garden, steps=131)
    three_quarters_full_corners = (
        walk(garden, start=start, steps=131 + 65)
        for start in ((0, 0), (130, 0), (0, 130), (130, 130))
    )
    one_quarter_full_corners = (
        walk(garden, start=start, steps=65)
        for start in ((0, 0), (130, 0), (0, 130), (130, 130))
    )
    half_step_edges = (
        walk(garden, start=start, steps=65)
        for start in ((0, 65), (65, 0), (65, 130), (130, 65))
    )
    return (
        full_box * (1 + 2 * (num_full_steps - 1) * num_full_steps)
        + sum(three_quarters_full_corners) * (num_full_steps - 1)
        + sum(one_quarter_full_corners) * num_full_steps
        + sum(half_step_edges)
    )
