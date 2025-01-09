#!/usr/bin/env python
"""
PART 1
Given orbital relationships, count total number of direct and indirect orbits

PART 2
Count orbital transfers to get YOU to orbit the same thing as SAN
"""
from collections import defaultdict
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
"""
PART_ONE_EXAMPLE_RESULT = 42
PART_ONE_RESULT = 144909
PART_TWO_EXAMPLE = """\
COM)B
B)C
C)D
D)E
E)F
B)G
G)H
D)I
E)J
J)K
K)L
K)YOU
I)SAN
"""
PART_TWO_EXAMPLE_RESULT = 4
PART_TWO_RESULT = 259


def parse(lines: Iterable[str]) -> dict[str, list[str]]:
    d = defaultdict(list)
    for line in lines:
        orbitee, orbiter = line.split(")")
        d[orbitee].append(orbiter)

    return d


def part_one(lines: Iterable[str]) -> int:
    orbits = parse(lines)
    orbit_counts = {"COM": 0}
    queue = ["COM"]
    while queue:
        orbitee = queue.pop()
        orbit_count = orbit_counts[orbitee]
        for orbiter in orbits[orbitee]:
            orbit_counts[orbiter] = orbit_count + 1
            queue.append(orbiter)

    return sum(orbit_counts.values())


def part_two(lines: Iterable[str]) -> int:
    orbits = parse(lines)

    sets = []
    queue = [["COM"]]
    while queue:
        orbit_sequence = queue.pop()

        orbiters = orbits.get(orbit_sequence[-1], [])
        if not orbiters:
            if orbit_sequence[-1] in {"YOU", "SAN"}:
                # Add nodes from COM to this node's parent
                sets.append(set(orbit_sequence[:-1]))
        else:
            for orbiter in orbiters:
                queue.append(orbit_sequence + [orbiter])

    # Symmetric difference to get count of nodes we need to hop
    return len(sets[0] ^ sets[1])
