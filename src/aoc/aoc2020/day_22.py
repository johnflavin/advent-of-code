#!/usr/bin/env python
"""
PART 1
Play war, but without wars

PART 2
Lots of new rules.
A game consists of rounds.
If a previous round in the game recurs, player 1 instantly wins the game.
Round proceeds as before, compare top cards.
If both players decks have at least as many cards as the number they just drew,
    recursively play a new game.
Otherwise (one player doesn't have enough cards) high card wins the round.
"""
import logging
from collections import deque
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
Player 1:
9
2
6
3
1

Player 2:
5
8
4
7
10
"""
PART_ONE_EXAMPLE_RESULT = 306
PART_ONE_RESULT = 34324
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 291
PART_TWO_RESULT = 33259

log = logging.getLogger(__name__)


def parse(lines: Iterable[str]) -> tuple[deque[int], deque[int]]:
    lines = iter(lines)
    _ = next(lines)  # Player 1:
    p1 = []
    for line in lines:
        if line == "":
            break
        p1.append(int(line))

    _ = next(lines)  # Player 2:
    p2 = []
    for line in lines:
        if line == "":
            break
        p2.append(int(line))

    return deque(p1), deque(p2)


def part_one(lines: Iterable[str]) -> int:
    player1, player2 = parse(lines)

    while player1 and player2:
        top1 = player1.popleft()
        top2 = player2.popleft()
        if top1 > top2:
            player1.extend((top1, top2))
        else:
            player2.extend((top2, top1))

    winner = player1 if player1 else player2
    return sum(card * (i + 1) for i, card in enumerate(reversed(winner)))


def part_two(lines: Iterable[str]) -> int:

    def game(deck1: deque[int], deck2: deque[int]) -> tuple[bool, deque[int]]:
        round_cache = set()
        while deck1 and deck2:
            log.debug("Player 1's deck: %s", deck1)
            log.debug("Player 2's deck: %s", deck2)
            # Check if we have played this round before
            round_ = tuple(deck1), tuple(deck2)
            if round_ in round_cache:
                return True, deck1
            round_cache.add(round_)

            # Pull cards
            top1 = deck1.popleft()
            top2 = deck2.popleft()
            log.debug("Player 1 plays: %d", top1)
            log.debug("Player 2 plays: %d", top2)

            if len(deck1) >= top1 and len(deck2) >= top2:
                # Play recursive game
                log.debug("Playing recursive game")
                player1_wins_round, _ = game(
                    deque(list(deck1)[:top1]), deque(list(deck2)[:top2])
                )
            else:
                # Compare cards
                player1_wins_round = top1 > top2

            if player1_wins_round:
                log.debug("Player 1 wins round")
                deck1.extend((top1, top2))
            else:
                log.debug("Player 2 wins round")
                deck2.extend((top2, top1))
        # Game over
        player1_wins_game = bool(deck1)
        log.debug("Player %d wins game", 1 if player1_wins_game else 2)
        return player1_wins_game, deck1 if player1_wins_game else deck2

    player1, player2 = parse(lines)
    _, winning_deck = game(player1, player2)
    log.debug("Winning deck %s", winning_deck)
    return sum(card * (i + 1) for i, card in enumerate(reversed(winning_deck)))
