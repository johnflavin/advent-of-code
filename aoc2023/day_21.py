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

Ok, I figured out what I was missing. In my part one solution I had hard-coded that
we would have to count spaces that are an even distance away from start.
That isn't always the case, though. It depends on the number of steps.
In fact, we are taking an odd number of steps in part two, so that's what we will need
to count in part 2.
...but that's not all! Because the length of a box is 131, which is odd,
that means when we cross box boundaries we have to flip from even to odd or odd to even.
Step 1: 1 odd
Step 2: 1 odd, 4 even
Step 3: 9 odd, 4 even
Step 4: 9 odd, 16 even

I see. So let's say we take N full steps. The number of full boxes of each type is
N^2 and (N-1)^2, but which one is the number of even and which is the number of odd
flips depending on whether N is even or odd.

The outer edge boxes will be the opposite even/oddness of N.
As will the 3/4 full corners.
The 1/4 full corners will be the same even/oddness as N.

Revised total:
Our total will be...
(odd full boxes: 131 steps, start middle) * 202300^2 +
(even full boxes: 132 steps, start middle) * 202299^2 +
(even 3/4 corners: 131 + 65 steps, start each corner + 1) * 202299 +
(odd 1/4 corners: 65 steps, start each corner) * 202300 +
(even edges: 65 steps, start middle of each edge + 1)

Answer: 601441112512888
Still too high. But I do think I'm getting closer.

Rather than fill the corners, let's subtract them off.
The number we can reach in a 3/4 full box starting from some corner is the number
    we can reach in a full box minus what we can reach from the opposite corner.
And since all the corners come in groups of four, we can use a 65 (or 64) step
    box subtracted from a full box to stand in for all four of the corners.
Ok... let's think this through.
For a group of 4 3/4 full corners, we treat them as 4 full boxes - one all-corner box.
And one all-corner box = 1 full box - a half box.
So 4 3/4 full corner boxes = 3 full boxes + one half box.

Similarly, four 1/4 full corners = one full box - one half box
Make sure I respect parity here.

What about edges? Opposite pairs = 2 full boxes - all-corner box = full + half
So for all four edges, we get 2 full + 2 half boxes

Let O be odd full box, o be odd half box, E full even, e half even.
Co = O - o = odd corner, Ce = E - e = even corner
N is number of full steps = 202300
Total
O * N^2 +
E * (N-1)^2 +
Ce * (N-1) +
Co * N +
2(O + o)
Answer: 601436570105532
Still not right. And I didn't get a "too high" or "too low".

O*N^2 + 2O*N + O = O*(N+1)^2
=> O*N^2 + O*N - o*N + 2O + 2o = O*(N+1)^2 - O*N - o*N + O + 2o
=  O*(N+1)^2 - Co*(N+1) + o
I don't like the leftover o. I don't think that is right.
E*(N-1)^2 = E*N^2 - 2E*(N-1) - E
=> E*(N-1)^2 + E*(N-1) - e*(N-1) = E*N^2 - Ce*(N-1) = E*N^2 - Ce*N + Ce

Ok, I think I am off by a bit.
The answer I have by my logic is
O*(N+1)^2 - Co*(N+1) + E*N^2 - Ce*N + o + Ce
I think the extra o and Ce are wrong. But I can't say why exactly.
It just doesn't look symmetric.
I'm going to try without.
Using just O*(N+1)^2 - Co*(N+1) + E*N^2 - Ce*N = 601439538229138, not right

Let's think about this a different way. We have this N+1 term showing up, so maybe
it would be easier to think about the number that would be full if we went one extra
full step.

I think I've got it.

On step 0 we are at even parity with start. When we take an even number of
steps we maintain that parity.
When we take N=202300 full steps, we are on another start with even parity.
Therefore in the even worlds, we need to take 65 steps and land on an odd parity space.
But when we think about the N+1 world and the corners to subtract, that is an odd
number of full steps and therefore an odd start. We would need to take an even number
of steps from that start to land on an odd space. So the full boxes of odd parity
need to count the even steps.

So how many boxes are there of each type? What's our formula?
With an even N, the edge worlds are even, the 3/4 corner worlds are even,
    but the 1/4 corner worlds are odd (meaning we want to know how far we can go in
    from a corner in 64 steps).
With even N*131 + 65, we have filled N^2 even boxes: E*N^2
We want to add N 1/4 corners of each type, i.e. N odd corner boxes: Co*N
If we were to take (N+1)*131 + 65 steps, we are in an odd parity world.
We would have filled (N+1)^2 odd boxes: O*(N+1)^2
But since we haven't gone that far, we have overcounted the corners on N-1 3/4 boxes.
However, we have also overcounted the corners on the edge boxes, two of each type,
    which makes a total of N+1 of each corner: Ce*(N+1)^2
Our formula then is O*(N+1)^2 + E*N^2 + Co*N - Ce*(N+1)^2

To find our counts we always start on start: (65, 65).
For E we are on an even parity start and must step an odd number, so step 129
For O we are on an odd parity start and must step an even number, so step 130
Co = O - o is the number within 64 of a corner.
So we must have o be the number 66 away from start.
Ce = E - e is the number within 65 of a corner.
So we must have e be the number 65 away from start.

Answer: 601441059120658
Incorrect, but I think I'm really really close
Oh, wait, I had a bug. I swapped which corner type had which N. Fixed that.
Answer: 601441025943376
Still not correct.

I think maybe my parity thinking was wrong.
I'm going to swap odd and even and see what that does for me.
Also I don't need to subtract the half full from the full to get the corners.
I have all the distances, so I can directly take all points at distance > 65 from start.
Answer: 601441063166538
Yep, that's the one.
"""

from .util import Coord
from collections import Counter, deque
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
PART_ONE_RESULT = 3598
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 6536
PART_TWO_EXAMPLE_STEPS = 100
PART_TWO_EXAMPLE_EXPANSION_FACTOR = 19
PART_TWO_RESULT = 601441063166538

OFFSETS = (
    (-1, 0),
    (0, -1),
    (1, 0),
    (0, 1),
)


def neighbors(pt: Coord) -> Iterable[Coord]:
    for row_off, col_off in OFFSETS:
        yield pt[0] + row_off, pt[1] + col_off


def walk(garden: list[str]) -> dict[int, int]:
    num_rows = len(garden)
    num_cols = len(garden[0])

    starts = [
        (row_idx, col_idx)
        for row_idx, line in enumerate(garden)
        for col_idx, ch in enumerate(line)
        if ch == "S"
    ]
    start = starts[0]

    dists = {}
    frontier = deque([(start, 0)])
    while frontier:
        pt, dist = frontier.popleft()

        if pt in dists and dist >= dists[pt]:
            continue

        if (
            not (-1 < pt[0] < num_rows and -1 < pt[1] < num_cols)
            or garden[pt[0]][pt[1]] == "#"
        ):
            continue

        dists[pt] = dist

        frontier.extend((neighbor, dist + 1) for neighbor in neighbors(pt))

    return Counter(dists.values())


def num_reachable(dists: dict[int, int], steps: int) -> int:
    return sum(
        count
        for dist, count in dists.items()
        if dist <= steps and (dist - steps) % 2 == 0
    )


def part_one(lines: Iterable[str]) -> int:
    garden = list(lines)
    dists = walk(garden)
    return num_reachable(dists, 64)


def part_two(lines: Iterable[str]) -> int:
    garden = list(lines)
    dists = walk(garden)

    # A hack to make my code work with the example
    # I want to do something a little different with the
    #   example than I'm going to do with the real thing,
    #   but I do still want to have a check.
    if len(garden) == PART_TWO_EXAMPLE.count("\n"):
        old_len = len(garden)
        garden = [
            (line * PART_TWO_EXAMPLE_EXPANSION_FACTOR).replace("S", ".")
            for _ in range(PART_TWO_EXAMPLE_EXPANSION_FACTOR)
            for line in garden
        ]
        start_pos = (old_len * PART_TWO_EXAMPLE_EXPANSION_FACTOR - 1) // 2
        garden[start_pos] = (
            garden[start_pos][:start_pos] + "S" + garden[start_pos][start_pos + 1 :]
        )
        dists = walk(garden)
        return num_reachable(dists, steps=PART_TWO_EXAMPLE_STEPS)

    assert len(garden) == 131

    num_full_steps = 202300

    # O: start is even parity, so step an odd number
    odd_full_box = sum(count for dist, count in dists.items() if dist % 2 == 1)

    # E: start is odd parity, so step an even number
    even_full_box = sum(count for dist, count in dists.items() if dist % 2 == 0)

    # Co: start is even parity, so step an odd number
    odd_corners = sum(
        count for dist, count in dists.items() if dist > 65 and dist % 2 == 1
    )

    # Ce: start is odd parity, so step an even number
    even_corners = sum(
        count for dist, count in dists.items() if dist > 65 and dist % 2 == 0
    )

    return (
        odd_full_box * (num_full_steps + 1) ** 2
        + even_full_box * num_full_steps**2
        - odd_corners * (num_full_steps + 1)
        + even_corners * num_full_steps
    )
