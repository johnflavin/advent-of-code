#!/usr/bin/env python
"""
PART 1
Given monkeys holding items of a certain value,
an operation for changing that value, a test for the value,
and another monkey to throw to given the result of the test.
Order of operations:
Inspect, divide value by 3, operation, test, throw

Count the number of inspections performed by the monkeys.
Answer: Multiply two highest inspection counts

PART 2
No longer divide value by 3, and go for 10000 rounds.
"You'll have to find some other way to reduce your worry".

If you try just not reducing the values, the numbers get very
big very quickly and everything slows down.
The key (without spoiling the answer) is to find a way to make the values smaller
without affecting any of the divisibility tests.
"""
import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

PART_ONE_EXAMPLE = """\
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
"""
PART_ONE_EXAMPLE_RESULT = 10605
PART_ONE_RESULT = 67830
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 2713310158
PART_TWO_RESULT = 15305381442


log = logging.getLogger(__name__)

MONKEY_IDX_RE = re.compile(r"Monkey (?P<idx>\d+):")
ITEMS_RE = re.compile(r"\s+Starting items: (?P<items>(\d+(, )?)+)")
OP_RE = re.compile(r"\s+Operation: new = (?P<op>.*)")
TEST_RE = re.compile(r"\s+Test: divisible by (?P<div>\d+)")
TEST_RESULT_RE = re.compile(r"\s+If (?P<tf>true|false): throw to monkey (?P<idx>\d+)")


@dataclass(repr=False)
class Monkey:
    idx: int
    items: list[int]
    op: str
    div: int
    true_dest: Self
    false_dest: Self
    round: int
    inspections: int = 0
    modulus: int = 1

    def __repr__(self):
        return (
            f"Monkey("
            f'idx={self.idx} items={self.items}, op="{self.op}", div={self.div}, '
            f"true->{self.true_dest.idx if self.true_dest else None}, "
            f"false->{self.false_dest.idx if self.false_dest else None}"
            f")"
        )

    def inspect(self):
        for value in self.items:
            self.inspections += 1
            value = eval(self.op, locals={"old": value})
            if self.round == 1:
                value = value // 3
            else:
                value = value % self.modulus
            divisible = value % self.div == 0
            dest = self.true_dest if divisible else self.false_dest
            dest.items.append(value)
        self.items = []


def parse(lines: Iterable[str], round: int) -> list[Monkey]:
    processing_monkey = False
    items = []
    op = None
    div = -1
    modulus = 1
    monkey_idx = -1
    dests: dict[(int, str), int] = {}
    monkeys = {}
    for line in lines:
        log.debug('processing line "%s"', line)
        if not line and processing_monkey:
            monkeys[monkey_idx] = Monkey(monkey_idx, items, op, div, None, None, round)
            processing_monkey = False
            log.debug("Finished processing monkey %s", monkeys[monkey_idx])
        elif (m := MONKEY_IDX_RE.match(line)) is not None:
            processing_monkey = True
            monkey_idx = int(m.group("idx"))
            # log.debug("Starting monkey %d", monkey_idx)
        elif (m := ITEMS_RE.match(line)) is not None:
            items = list(map(int, m.group("items").split(", ")))
            # log.debug("items %s", items)
        elif (m := OP_RE.match(line)) is not None:
            op = m.group("op")
            # log.debug("op \"%s\"", op)
        elif (m := TEST_RE.match(line)) is not None:
            div = int(m.group("div"))
            modulus *= div
            # log.debug("div %d", div)
        elif (m := TEST_RESULT_RE.match(line)) is not None:
            tf = m.group("tf")
            dest_idx = int(m.group("idx"))
            dests[(monkey_idx, tf)] = dest_idx
            # log.debug("If %s -> %d", tf, dest_idx)
        else:
            if line:
                raise RuntimeError("Did not correctly parse line")
    if processing_monkey:  # There may be one left over if there wasn't a blank line
        monkeys[monkey_idx] = Monkey(monkey_idx, items, op, div, None, None, round)
        log.debug("Finished processing monkey %s", monkeys[monkey_idx])

    for (source_idx, tf), dest_idx in dests.items():
        source_monkey = monkeys[source_idx]
        source_monkey.modulus = modulus
        if tf == "true":
            source_monkey.true_dest = monkeys[dest_idx]
        else:
            source_monkey.false_dest = monkeys[dest_idx]

    log.debug("Monkeys: %s", monkeys)
    return list(monkeys.values())


def part_one(lines: Iterable[str]) -> int:
    monkeys = parse(lines, 1)
    for _round in range(20):
        log.debug("Round %d", _round + 1)
        for monkey in monkeys:
            monkey.inspect()

    inspected = sorted([monkey.inspections for monkey in monkeys])
    return inspected[-1] * inspected[-2]


def part_two(lines: Iterable[str]) -> int:
    monkeys = parse(lines, 2)
    for _round in range(10000):
        for monkey in monkeys:
            monkey.inspect()

    inspected = sorted([monkey.inspections for monkey in monkeys])
    return inspected[-1] * inspected[-2]
