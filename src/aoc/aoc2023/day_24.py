#!/usr/bin/env python
"""

PART 1
Given lines of hailstones initial x,y,z and velocity vx,vy,vz at time t=0.
Also, out of band, given limits on the x,y area to search (ignore z).

Examine pairs of hailstones.
Find how many pairs' paths will intersect in the future within the test area.
(And I think that if a given hailstone X intersects A at time ta and B at time tb,
we only count X once for the earliest intersection.)

PART 2
At what initial position and velocity could you throw a rock that would hit
all the hailstones?

Sum the x, y, and z of the initial position.

SOLUTION
This took me a long time to solve. I finally cracked it on Jan. 4, 2024.

The idea is this. For every hailstone, we will have a (vector) equation:
P + ti*V = Pi + ti*Vi

Where P and V are the unknown rock position and velocity,
P = (px, py, pz); V = (vx, vy, vz)
Pi and Vi are the known position and velocity of hailstone i,
Pi = (pix, piy, piz); Vi = (vix, viy, viz)
and ti is the time it takes for them to intersect.

From this we can immediately see that the vector components all must be equal.
That gives us equations for ti and some of the components:
ti = -(px-pix)/(vx-vix) = -(py-piy)/(vy-viy) = -(pz-piz)/(vz-viz)

With a single hailstone, we get two unique equations for the p and v components.
The third is redundant. But that lets us eliminate two of the components,
say vx and vy, in terms of vz and the ps.

We will get the rest of the information by considering more than one hailstone.
We connect an arbitrary pair i,j.
Say we start from

    (vx-vix)/(px-pix) = (vz-viz)/(pz-piz)
    (vy-viy)/(py-piy) = (vz-viz)/(pz-piz)
    (vy-vjy)/(py-pjy) = (vx-vjx)/(px-pjx)

By substituting the first two into the third we can show that

(1) (vz-viz)/(pz-piz) =
        [(viy-vjy)(px-pjx)+(vjx-vix)(py-pjy)]/[(px-pix)(py-pjy)-(py-piy)(px-pjx)]

This is symmetric under exchange of x and y. The numerator and denominator
both pick up a negative, which cancel.
But it is not symmetric under exchange of i and j. If we exchange those indices, we get

(2) (vz-vjz)/(pz-pjz) =
        [(viy-vjy)(px-pix)+(vjx-vix)(py-piy)]/[(px-pix)(py-pjy)-(py-piy)(px-pjx)]

which is not the same RHS as (1). They have the same denominator
but different numerators. However, these two must be the same.
i and j are arbitrary labels; so long as they aren't equal they can be anything,
so choosing i first then j must be equivalent to choosing j first then i.

(Later note: I'm not so sure anymore that these are actually equivalent.
In my prose I'm relying on being able to reassign labels, which is fine in general,
but once you use those labels in a single expression they really aught to
mean the same thing or you're writing nonsense. And in fact, if we do treat i as
a particular hailstone and j as a different particular hailstone, then
(vz-viz)/(pz-piz) = -1/ti which is definitely not equal to
(vz-vjz)/(pz-pjz) = -1/tj. However, while I think my
motivating reasoning is questionable at best,
there is no fault in the algebraic manipulations.
I'm subtracting (2) from (1), which as long as I do the same thing
to both sides of the equation is a valid thing to do.
I no longer know why one would want to do that, but I did it,
and it gave me an invariant that I can use to find the answer.
So... that's cool I guess.)

What we'll do is subtract the two equations: (1) - (2).
After expanding everything out and grouping terms (which I won't show)
there are nice cancellations. All the vz terms go away, as do terms
quadratic in the p components.
What we are left with can be written as

(3) (Vi-Vj)×(Pi-Pj)⋅P = (Vi-Vj)⋅Pi×Pj

Everything in this equation is known except for P,
meaning this is what we need to solve.
P has three unknown components, so we need three equations.
We get those by selecting any three hailstones 0, 1, and 2
and grouping them into three pairs i=0, j=1; i=0, j=2; and i=1, j=2.
Each one of those i,j pairs gives us another equation from (3).
We organize those as rows of a single matrix equation

    C P = D

Where the rows of matrix C are the (Vi-Vj)×(Pi-Pj) vectors, and
the components of vector D are the (Vi-Vj)⋅Pi×Pj scalars.

The answer we are looking for is

    P = C^-1 D

In the code I've written out that matrix inverse by hand.
Yes, I'm aware I could use numpy. But I did the math by hand,
so why not just finish the job?
"""

import logging
from .util import Coord
from collections.abc import Iterable
from itertools import combinations
from math import sumprod


PART_ONE_EXAMPLE = """\
19, 13, 30 @ -2,  1, -2
18, 19, 22 @ -1, -1, -2
20, 25, 34 @ -2, -2, -4
12, 31, 28 @ -1, -2, -1
20, 19, 15 @  1, -5, -3
"""
PART_ONE_EXAMPLE_TEST_AREA = [7, 27]
PART_ONE_EXAMPLE_RESULT = 2
PART_ONE_TEST_AREA = [200000000000000, 400000000000000]
PART_ONE_RESULT = 21785
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 47
PART_TWO_RESULT = 554668916217145


log = logging.getLogger(__name__)

type Vector = tuple[int, int, int]


def find_intersection(
    xy0: Coord, vxvy0: Coord, xy1: Coord, vxvy1: Coord
) -> tuple[float, float, float, float] | tuple[None, None, None, None]:
    """
    X = Vt + X0 => t = (X-X0)/V
    y = vy/vx(x-x0) + y0 = v(x-x0) + y0 (using v=vy/vx)
    If we have two of these, they intersect at
    v0(x-x0) + y0 = v1(x-x1) + y1
    => (v0-v1)x = v0*x0-v1*x1 + y1-y0
    => x = (v0*x0-v1*x1 + y1-y0)/(v0-v1)
    and plugging in for y (using v0, though we should be able to use either)
    y = v0(x-x0) + y0 = v0*x - v0*x0 + y0
      = v0[(v0*x0-v1*x1 + y1-y0)/(v0-v1) - x0] + y0
      = (v0*v1*(x0-x1) + v0*y1 - v1*y0)/(v0-v1)

    We won't have any intersection if v0 == v1
    """
    x0, y0 = xy0
    x1, y1 = xy1
    vx0, vy0 = vxvy0
    vx1, vy1 = vxvy1
    v0 = vy0 / vx0
    v1 = vy1 / vx1
    if v0 == v1:
        # No intersection
        return None, None, None, None
    x = (v0 * x0 - v1 * x1 + y1 - y0) / (v0 - v1)
    y = (v0 * y1 - v1 * y0 + (x0 - x1) * v0 * v1) / (v0 - v1)
    t0 = (x - x0) / vx0
    t1 = (x - x1) / vx1
    return x, y, t0, t1


def parse(line: str) -> tuple[Vector, Vector]:
    pos, vel = line.split(" @ ")
    pos: Vector = tuple(map(int, pos.split(", ")))
    vel: Vector = tuple(map(int, vel.split(", ")))
    return pos, vel


def part_one(lines: Iterable[str]) -> int:
    position_velocity_pairs = []
    for line in lines:
        xyz, vxyz = parse(line)
        position_velocity_pairs.append((xyz[:-1], vxyz[:-1]))

    # Hack to have example and test use parameters that aren't in the input
    if len(position_velocity_pairs) == PART_ONE_EXAMPLE.count("\n"):
        lower, upper = PART_ONE_EXAMPLE_TEST_AREA
    else:
        lower, upper = PART_ONE_TEST_AREA

    intersections = [
        (*pv0, *pv1, *find_intersection(*pv0, *pv1))
        for pv0, pv1 in combinations(position_velocity_pairs, 2)
    ]

    total = 0
    for xy0, v0, xy1, v1, x, y, t0, t1 in intersections:
        # print(f"(x0,y0)={xy0} (vx0,vy0)={v0} (x1,y1)={xy1} (vx1,vy1)={v1}")
        # print(f"intersection: (x,y)=({x},{y}) at t0={t0}, t1={t1}")
        # print()
        if x is None or y is None or t0 is None or t1 is None:
            # Parallel lines
            # print("Parallel lines")
            continue
        elif t0 < 0 or t1 < 0:
            # Intersection is at negative time
            # print("Negative time")
            continue
        elif not (lower <= x <= upper and lower <= y <= upper):
            # Intersection is outside bounds
            # print("Outside bounds")
            continue
        # print("Good intersection")
        total += 1

    return total


def intial_position(
    p0: Vector, v0: Vector, p1: Vector, v1: Vector, p2: Vector, v2: Vector
) -> Vector:
    def delta(vec_i, vec_j):
        return tuple(va - vb for va, vb in zip(vec_i, vec_j))

    def cross(vect_i, vec_j):
        return (
            vect_i[1] * vec_j[2] - vect_i[2] * vec_j[1],
            vect_i[2] * vec_j[0] - vect_i[0] * vec_j[2],
            vect_i[0] * vec_j[1] - vect_i[1] * vec_j[0],
        )

    log.debug("p0 v0 = %s %s", p0, v0)
    log.debug("p1 v1 = %s %s", p1, v1)
    log.debug("p2 v2 = %s %s", p2, v2)

    dv01 = delta(v0, v1)
    dv02 = delta(v0, v2)
    dv12 = delta(v1, v2)
    c01 = cross(dv01, delta(p0, p1))
    c02 = cross(dv02, delta(p0, p2))
    c12 = cross(dv12, delta(p1, p2))
    dvij_dot_pi_cross_pj = (
        sumprod(dv01, cross(p0, p1)),
        sumprod(dv02, cross(p0, p2)),
        sumprod(dv12, cross(p1, p2)),
    )
    if log.isEnabledFor(logging.DEBUG):
        log.debug("p0-p1 = %s", delta(p0, p1))
        log.debug("p0-p2 = %s", delta(p0, p2))
        log.debug("p1-p2 = %s", delta(p1, p2))
        log.debug("v0-v1 = %s", dv01)
        log.debug("v0-v2 = %s", dv02)
        log.debug("v1-v2 = %s", dv12)
        log.debug("c01 = (v0-v1)×(p0-p1) = %s", c01)
        log.debug("c02 = (v0-v2)×(p0-p2) = %s", c02)
        log.debug("c12 = (v1-v2)×(p1-p2) = %s", c12)
        log.debug("(v0-v1)⋅p0×p1 = %s", dvij_dot_pi_cross_pj[0])
        log.debug("(v0-v2)⋅p0×p2 = %s", dvij_dot_pi_cross_pj[1])
        log.debug("(v1-v2)⋅p1×p2 = %s", dvij_dot_pi_cross_pj[2])

    c_inverse_unnorm = (
        (
            c12[1] * c02[2] - c12[2] * c02[1],
            c01[1] * c12[2] - c01[2] * c12[1],
            c01[2] * c02[1] - c01[1] * c02[2],
        ),
        (
            c12[2] * c02[0] - c12[0] * c02[2],
            c01[2] * c12[0] - c01[0] * c12[2],
            c01[0] * c02[2] - c01[2] * c02[0],
        ),
        (
            c12[0] * c02[1] - c12[1] * c02[0],
            c01[0] * c12[1] - c01[1] * c12[0],
            c01[1] * c02[0] - c01[0] * c02[1],
        ),
    )
    log.debug("c inverse unnorm = %s", c_inverse_unnorm)
    determinant = sum(c01[i] * c_inverse_unnorm[i][0] for i in range(3))
    log.debug("|C| = %s", determinant)

    p: Vector = tuple(
        sumprod(c_inverse_row, dvij_dot_pi_cross_pj) // determinant
        for c_inverse_row in c_inverse_unnorm
    )

    if log.isEnabledFor(logging.DEBUG):
        log.debug("p = %s", p)
        log.debug("Sanity check")
        lhs = (
            sumprod(c01, p),
            sumprod(c02, p),
            sumprod(c12, p),
        )
        ij = ((0, 1), (0, 2), (1, 2))
        for left, right, (i, j) in zip(lhs, dvij_dot_pi_cross_pj, ij):
            eq_str = "=" if left == right else "!"
            log.debug(
                "(v%d-v%d)×(p%d-p%d)⋅p = %s %s= %s", i, j, i, j, left, eq_str, right
            )

    return p


def part_two(lines: Iterable[str]) -> int:
    position_velocity_pairs: list[tuple[Vector, Vector]] = []
    for line in lines:
        position_velocity_pairs.append(parse(line))

    p = intial_position(
        *position_velocity_pairs[0],
        *position_velocity_pairs[1],
        *position_velocity_pairs[2],
    )
    return sum(p)
