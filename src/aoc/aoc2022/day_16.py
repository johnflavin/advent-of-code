#!/usr/bin/env python
"""
PART 1
Given a set of valves which can release pressure if opened
and the connecting tunnels between valves, figure out a route
through the tunnels that releases the maximum pressure.
You have 30 minutes. Moving between tunnels takes one minute,
and opening a valve takes one minute.
Once a valve is open, the pressure release accumulates each minute.

PART 2
Spend the first four minutes teaching an elephant to help you.
Now you have 26 minutes but can do two things in parallel.
"""
import logging
import re
from collections.abc import Iterable
from typing import Any

PART_ONE_EXAMPLE = """\
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
"""
PART_ONE_EXAMPLE_RESULT = 1651
PART_ONE_RESULT = 1880
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 1707
PART_TWO_RESULT = 2520


log = logging.getLogger(__name__)


GRAPH_LINE_RE = re.compile(
    r"Valve (?P<name>[A-Z]+) has flow rate=(?P<rate>\d+); "
    + r"tunnel(s?) lead(s?) to valve(s?) (?P<neighbors>(([A-Z]+)(, )?)+)"
)


def dp_max_score(graph, start, max_steps):
    """
    Dynamic Programming solution to maximize compounding scores
    within a given number of steps.

    :param graph: A dictionary where keys are nodes and values are dictionaries with:
                  'score': The node's score,
                  'neighbors': A list of adjacent node labels.
    :param start: The starting node.
    :param max_steps: The maximum number of steps allowed.
    :return: The maximum score achievable within the step constraint.
    """
    # cache: {(node, steps_remaining, frozenset(activated_nodes)): max_score}
    cache = {}

    def dp(node, steps_remaining, activated_nodes):
        # If we've already computed this state, return its value
        state = (node, steps_remaining, activated_nodes)
        if state in cache:
            return cache[state]

        # Base case: No steps remaining
        if steps_remaining == 0:
            return 0

        # # Current node's score contribution (if activated)
        # score_from_activation = 0
        # if node not in activated_nodes and steps_remaining >= 2:
        #     score_from_activation = graph[node]['score'] * (steps_remaining - 1)

        # Option 1: Move to a neighbor without activating
        score1 = max(
            dp(neighbor, steps_remaining - 1, activated_nodes)
            for neighbor in graph.get(node, {}).get("neighbors", [])
        )

        # Option 2: Activate this node and stay
        score2 = 0
        if (score := graph[node]["score"]) > 0 and node not in activated_nodes:
            new_activated_nodes = activated_nodes | {node}
            score2 = score * (steps_remaining - 1) + dp(
                node, steps_remaining - 1, new_activated_nodes
            )

        # Store the result in the DP table
        max_score = max(score1, score2)
        cache[state] = max_score
        return max_score

    # Start the DP recursion
    return dp(start, max_steps, frozenset())


def dp_max_score_parallel(graph, start, max_steps):
    """
    Dynamic Programming solution to maximize compounding scores
    within a given number of steps.
    ...but this time you have an elephant.

    :param graph: A dictionary where keys are nodes and values are dictionaries with:
                  'score': The node's score,
                  'neighbors': A list of adjacent node labels.
    :param start: The starting node.
    :param max_steps: The maximum number of steps allowed.
    :return: The maximum score achievable within the step constraint.
    """
    # cache: {(node1, node2, steps_remaining, frozenset(activated_nodes)): max_score}
    cache = {}
    all_activated = set(node for node, info in graph.items() if info["score"] > 0)

    def dp(node1, node2, steps_remaining, activated_nodes):
        # If we've already computed this state, return its value
        if (state := (node1, node2, steps_remaining, activated_nodes)) in cache:
            return cache[state]
        # ... but we could also get to this state in the other order, so
        # check for that too
        if (state2 := (node2, node1, steps_remaining, activated_nodes)) in cache:
            return cache[state2]

        # Base case: No steps remaining
        if steps_remaining == 0:
            return 0

        # Another base case: all valves turned on
        if activated_nodes == all_activated:
            return 0

        # Option 1: Move to a neighbor without activating (both)
        score1 = max(
            dp(neighbor1, neighbor2, steps_remaining - 1, activated_nodes)
            for neighbor1 in graph.get(node1, {}).get("neighbors", [])
            for neighbor2 in graph.get(node2, {}).get("neighbors", [])
        )

        # Option 2: Activate this node and stay (both)
        score2 = 0
        if (
            node1 != node2  # Can't both activate at the same time
            and (node_score1 := graph[node1]["score"]) > 0
            and (node_score2 := graph[node2]["score"]) > 0
            and node1 not in activated_nodes
            and node2 not in activated_nodes
        ):
            new_activated_nodes = activated_nodes | {node1, node2}
            score2 = (node_score1 + node_score2) * (steps_remaining - 1) + dp(
                node1, node2, steps_remaining - 1, new_activated_nodes
            )

        # Option 3: 1 Moves to a neighbor, 2 activates
        score3 = 0
        if (node_score2 := graph[node2]["score"]) > 0 and node2 not in activated_nodes:
            new_activated_nodes = activated_nodes | {node2}
            score3 = node_score2 * (steps_remaining - 1) + max(
                dp(neighbor1, node2, steps_remaining - 1, new_activated_nodes)
                for neighbor1 in graph.get(node1, {}).get("neighbors", [])
            )

        # Option 4: 1 activates, 2 moves to a neighbor
        score4 = 0
        if (node_score1 := graph[node1]["score"]) > 0 and node1 not in activated_nodes:
            new_activated_nodes = activated_nodes | {node1}
            score4 = node_score1 * (steps_remaining - 1) + max(
                dp(node1, neighbor2, steps_remaining - 1, new_activated_nodes)
                for neighbor2 in graph.get(node2, {}).get("neighbors", [])
            )

        # Store the result in the DP table
        max_score = max(score1, score2, score3, score4)
        log.debug("score=%d state=%s", max_score, state)
        cache[state] = max_score
        return max_score

    # Start the DP recursion
    return dp(start, start, max_steps, frozenset())


def parse_graph(lines: Iterable[str]) -> dict[str, dict[str, Any]]:
    return {
        m.group("name"): {
            "score": int(m.group("rate")),
            "neighbors": m.group("neighbors").split(", "),
        }
        for line in lines
        if (m := GRAPH_LINE_RE.match(line)) is not None
    }


def part_one(lines: Iterable[str]) -> int:
    graph = parse_graph(lines)

    return dp_max_score(graph, "AA", 30)


def part_two(lines: Iterable[str]) -> int:
    graph = parse_graph(lines)
    return dp_max_score_parallel(graph, "AA", 26)
