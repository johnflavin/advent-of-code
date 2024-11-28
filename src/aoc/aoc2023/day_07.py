#!/usr/bin/env python
"""

PART 1
Given list of hands and bids.

Hands are ranked kinda like poker.
- Five of a kind    (7)
- Four of a kind    (6)
- Full house        (5)
- Three of a kind   (4)
- Two pair          (3)
- One pair          (2)
- High card         (1)

On a tie, hands are ranked by first card, then second, and so on.

Once hands are sorted into ranks (1 through N) their score is rank * bid.
Total the scores.

PART 2
J is not Jack but Joker.
Jokers can be any card that would make the hand type strongest.
But when breaking ties within hand type, jokers are the weakest card.
"""

from collections import Counter
from collections.abc import Iterable
from functools import cached_property, total_ordering


PART_ONE_EXAMPLE = """\
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
"""
PART_ONE_EXAMPLE_RESULT = 6440
PART_ONE_RESULT = 253866470
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 5905
PART_TWO_RESULT = 254494947


card_ranks_no_jokers = {
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "6": 5,
    "7": 6,
    "8": 7,
    "9": 8,
    "T": 9,
    "J": 10,
    "Q": 11,
    "K": 12,
    "A": 13,
}

card_ranks_w_jokers = {
    "2": 1,
    "3": 2,
    "4": 3,
    "5": 4,
    "6": 5,
    "7": 6,
    "8": 7,
    "9": 8,
    "T": 9,
    "J": 0,
    "Q": 11,
    "K": 12,
    "A": 13,
}


def hand_type_no_jokers(counts: Counter) -> int:
    count_values = counts.values()
    count_len = len(count_values)
    if count_len == 1:  # 5
        return 7
    if 4 in count_values:  # 4, 1
        return 6
    if count_len == 2:  # 3, 2
        return 5
    if 3 in count_values:  # 3, 1, 1
        return 4
    if count_len == 3:  # 2, 2, 1
        return 3
    if count_len == 4:  # 2, 1, 1, 1
        return 2
    return 1  # 1, 1, 1, 1, 1


def hand_type_w_jokers(counts: Counter) -> int:
    num_jokers = counts.pop("J")
    if num_jokers == 5:
        return 7
    most_common = counts.most_common(1)  # [(card, count)]
    most_common_card = most_common[0][0]
    counts[most_common_card] += num_jokers
    return hand_type_no_jokers(counts)


@total_ordering
class Hand:
    cards: str
    card_ranks: list[int]
    bid: int
    consider_jokers: bool

    def __init__(self, cards: str, bid: str, consider_jokers=False):
        self.cards = cards
        self.bid = int(bid)
        self.consider_jokers = consider_jokers
        card_ranks = (
            card_ranks_w_jokers if self.consider_jokers else card_ranks_no_jokers
        )
        self.card_ranks = [card_ranks[card] for card in cards]

    @cached_property
    def rank_type(self):
        counts = Counter(self.cards)
        if not self.consider_jokers or "J" not in counts:
            return hand_type_no_jokers(counts)
        else:
            return hand_type_w_jokers(counts)

    def __lt__(self, other: "Hand"):
        if self.rank_type < other.rank_type:
            return True
        if self.rank_type > other.rank_type:
            return False
        for self_card_rank, other_card_rank in zip(self.card_ranks, other.card_ranks):
            if self_card_rank < other_card_rank:
                return True
            if self_card_rank > other_card_rank:
                return False
        return False

    def __eq__(self, other: "Hand"):
        return self.rank_type == other.rank_type and self.cards == other.cards


def part_one(lines: Iterable[str]) -> int:
    hands = sorted(Hand(*line.split()) for line in lines if line)
    return sum(hand.bid * (idx + 1) for idx, hand in enumerate(hands))


def part_two(lines: Iterable[str]) -> int:
    hands = sorted(Hand(*line.split(), consider_jokers=True) for line in lines if line)
    return sum(hand.bid * (idx + 1) for idx, hand in enumerate(hands))
