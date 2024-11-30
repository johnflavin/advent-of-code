#!/usr/bin/env python
"""

PART 1
We are given a path with a loop.
Find the distance of the furthest point on the loop from the start.

Solution Discussion
I can load the path into a networkx Graph pretty easily.
And I bet there is some function in there that could give me what I want.
Unfortunately, I do not know what it is.
It seems like a want a path that is simultaneously the longest—in that I want
    to find points that are far away—and the shortest—in that if there are two ways
    to reach a point we always want to use the lowest possible distance value.

I could use Dijkstra to find the shortest path. But I don't think that is correct.
If there are two loops that both include the start point, Dijkstra would give us
the smaller one, but we want the bigger one.

Maybe the simple_cycles function in networkx will give me what I want.
If I take the longest cycle... That won't be correct actually.
For a given node, I want its distance to be assigned based on the shortest cycle
in which it appears, not the longest.
So if there is a cycle of length N and an almost identical cycle with a little
side bump of length N+2, I want the distances of all nodes not in the side bump
to be based on the length-N cycle.

Ok, here's what I do.
Find all cycles.
Keep a map of farthest node in each cycle to its distance
Load the map in a loop over cycles ordered by decreasing length.
    At each cycle, see if any of the "farthest" nodes are in this map with a shorter
        distance than what we think. If so, update.
Find the longest distance value and return

Eh, this isn't working. There are too many cycles and
    I don't really know what I'm supposed to do with them.

But I can return to dijkstra. There is a single_source_dijkstra that will
    give me paths and distances to all nodes from start. Seems useful.

...I've tried like five different things and I can't get the right answer.
If I use dijkstra to find the farthest point from start, I get 397. That's too low.
When I try to find cycles and take the biggest one that includes start, I get 2151.
And that's too low as well, it seems.
I don't know what else I'm supposed to do here.
Unless I'm parsing the input wrong, or building the graph wrong.

...Oh, yes. I see. I absolutely am building the graph wrong.
I'm making edges based on what each pipe says it is. But that assumes the
node on the other end of that edge correctly hooks up to it.
But it doesn't always happen that way. I need to check that.
When building the graph I can just add nodes no problem. But to add an edge
I need to confirm the connection.

After fixing my edge creation, I got a lot closer. Then had to fix it a little more.
Now I got the answer for part one.
Turns out multiple of the methods I tried work correctly to find the answer.
Once I have the right input, that is.

PART 2
How many tiles are enclosed by the loop?

Traverse the cycle, keeping track of turns, and adding points to a left and right set.
Once we know if we are left- or right-handed, the left or right set will be inside.
Then look through all those inside points, adding potential neighbors, removing pipe
points.
Size of set is number inside.
"""

import networkx as nx
from collections.abc import Iterable
from networkx import Graph

from aoc.util import Coord


PART_ONE_EXAMPLE = """\
..F7.
.FJ|.
SJ.L7
|F--J
LJ...
"""
PART_ONE_EXAMPLE_RESULT = 8
PART_ONE_RESULT = 7086  # Not 397, not 2151, not 14171
PART_TWO_EXAMPLE = """\
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L
"""
PART_TWO_EXAMPLE_RESULT = 10
PART_TWO_RESULT = 317


DIST = "distance"
VISITED = "visited"


def parse(lines: Iterable[str]) -> tuple[Graph, Coord]:
    graph = Graph()
    start = None
    for row, line in enumerate(lines):
        for col, ch in enumerate(line):
            if ch == ".":
                continue

            node = (row, col)
            graph.add_node(node, symbol=ch)

            if ch == "S":
                start = node

                u = (row, col - 1)
                if u in graph:
                    u_ch = graph.nodes[u]["symbol"]
                    if u_ch in {"-", "L", "F"}:
                        graph.add_edge(u, node)
                u = (row - 1, col)
                if u in graph:
                    u_ch = graph.nodes[u]["symbol"]
                    if u_ch in {"|", "7", "F"}:
                        graph.add_edge(u, node)
            else:
                if ch == "-":
                    for u_col in (-1, +1):
                        u = (row, col + u_col)
                        if u in graph:
                            u_ch = graph.nodes[u]["symbol"]
                            if u_ch in {"-", "F", "J", "L", "7", "S"}:
                                graph.add_edge(u, node)
                elif ch == "|":
                    for u_row in (-1, +1):
                        u = (row + u_row, col)
                        if u in graph:
                            u_ch = graph.nodes[u]["symbol"]
                            if u_ch in {"|", "F", "J", "L", "7", "S"}:
                                graph.add_edge(u, node)
                elif ch == "F":
                    u = (row, col + 1)
                    if u in graph:
                        u_ch = graph.nodes[u]["symbol"]
                        if u_ch in {"-", "J", "7", "S"}:
                            graph.add_edge(u, node)
                    u = (row + 1, col)
                    if u in graph:
                        u_ch = graph.nodes[u]["symbol"]
                        if u_ch in {"|", "J", "L", "S"}:
                            graph.add_edge(u, node)
                elif ch == "7":
                    u = (row, col - 1)
                    if u in graph:
                        u_ch = graph.nodes[u]["symbol"]
                        if u_ch in {"-", "L", "F", "S"}:
                            graph.add_edge(u, node)
                    u = (row + 1, col)
                    if u in graph:
                        u_ch = graph.nodes[u]["symbol"]
                        if u_ch in {"|", "J", "L", "S"}:
                            graph.add_edge(u, node)
                elif ch == "J":
                    u = (row, col - 1)
                    if u in graph:
                        u_ch = graph.nodes[u]["symbol"]
                        if u_ch in {"-", "L", "F", "S"}:
                            graph.add_edge(u, node)
                    u = (row - 1, col)
                    if u in graph:
                        u_ch = graph.nodes[u]["symbol"]
                        if u_ch in {"|", "7", "F", "S"}:
                            graph.add_edge(u, node)
                elif ch == "L":
                    u = (row, col + 1)
                    if u in graph:
                        u_ch = graph.nodes[u]["symbol"]
                        if u_ch in {"-", "J", "7", "S"}:
                            graph.add_edge(u, node)
                    u = (row - 1, col)
                    if u in graph:
                        u_ch = graph.nodes[u]["symbol"]
                        if u_ch in {"|", "7", "F", "S"}:
                            graph.add_edge(u, node)
                else:
                    raise ValueError(f"Parse error at {row},{col} symbol {ch}")
    if not start:
        raise ValueError("Did not find start node in graph")
    return graph, start


def part_one(lines: Iterable[str]) -> int:
    graph, start = parse(lines)
    cycle = nx.find_cycle(graph, source=start)
    return len(cycle) // 2


def part_two(lines: Iterable[str]) -> int:
    graph, start = parse(lines)
    cycle = nx.find_cycle(graph, source=start)
    cycle_nodes = set()
    for edge in cycle:
        cycle_nodes.add(edge[0])
        cycle_nodes.add(edge[1])

    # Find number of turns around the cycle.
    # +1 for each right, -1 for each left.
    # +4 means we are right-handed, -4 means left.
    # (Though we may be off by one because start could be a turn and we don't count it)
    turns = 0

    # Make sets of points to check: left and right
    # If we find that the shape is left-handed, then left will be the points inside.
    # Otherwise right is inside.
    left = set()
    right = set()

    # Traverse the cycle edges
    for prev_node, node in cycle:
        symbol = graph.nodes[node]["symbol"]
        direction = (node[0] - prev_node[0], node[1] - prev_node[1])
        north = (node[0] - 1, node[1])
        south = (node[0] + 1, node[1])
        east = (node[0], node[1] + 1)
        west = (node[0], node[1] - 1)
        if symbol == "|":
            if direction == (1, 0):
                left.add(east)
                right.add(west)
            elif direction == (-1, 0):
                left.add(west)
                right.add(east)
            else:
                raise Exception(f"Unexpected direction {direction} for symbol {symbol}")
        elif symbol == "-":
            if direction == (0, 1):
                left.add(north)
                right.add(south)
            elif direction == (0, -1):
                left.add(south)
                right.add(north)
            else:
                raise Exception(f"Unexpected direction {direction} for symbol {symbol}")
        elif symbol == "J":
            if direction == (0, 1):
                right.add(south)
                right.add(east)
                turns += -1
            elif direction == (1, 0):
                left.add(south)
                left.add(east)
                turns += 1
            else:
                raise Exception(f"Unexpected direction {direction} for symbol {symbol}")
        elif symbol == "F":
            if direction == (0, -1):
                right.add(north)
                right.add(west)
                turns += -1
            elif direction == (-1, 0):
                left.add(west)
                left.add(north)
                turns += 1
            else:
                raise Exception(f"Unexpected direction {direction} for symbol {symbol}")
        elif symbol == "L":
            if direction == (0, -1):
                left.add(south)
                left.add(west)
                turns += 1
            elif direction == (1, 0):
                right.add(south)
                right.add(west)
                turns += -1
            else:
                raise Exception(f"Unexpected direction {direction} for symbol {symbol}")
        elif symbol == "7":
            if direction == (0, 1):
                left.add(north)
                left.add(east)
                turns += 1
            elif direction == (-1, 0):
                right.add(north)
                right.add(east)
                turns += -1
            else:
                raise Exception(f"Unexpected direction {direction} for symbol {symbol}")

    inside = (right if turns > 0 else left).difference(cycle_nodes)

    tested = set()
    queue = list(inside)
    while queue:
        node = queue.pop()
        if node in tested:
            continue
        tested.add(node)
        if node in cycle_nodes:
            continue
        inside.add(node)
        neighbors = {
            (node[0] + 1, node[1]),
            (node[0] - 1, node[1]),
            (node[0], node[1] - 1),
            (node[0], node[1] + 1),
        }
        queue.extend(neighbors)

    return len(inside)
