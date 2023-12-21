#!/usr/bin/env python
"""

PART 1
The input is a bunch of modules wired together.
They can send low pulses and high pulses.

If a module's name starts with % it is a "flip flop" module.
It ignores high pulses.
When it receives a low pulse it flips from off to on and sends a high pulse.
When it received a low pulse again it flips from on to off and sends a low pulse.

If the name starts with & it is a conjunction module.
It remembers the last pulse from all its inputs, defaulting to low.
When each pulse is received, it updates it memory for that input.
At that time if it remembers high pulses for all inputs, it sends a low pulse.
Otherwise it sends a high pulse.

There is a single broadcaster module, which sends the pulse it receives to all
destination modules.
And there is a single button module that sends a low pulse to the broadcaster module.

All pulses are processed in the order they are received.
So if module X sends pulses to modules A, B, and C, those three must be
sent and received and handled before any pulses from module A are sent, and so on.

We push the button 1000 times. How many high pulses and low pulses are sent?
Answer is the product of high and low pulses.

PART 2
How many clicks of the button will it take for node "rx" to produce a high pulse?

Clearly we can't run this brute force.
It looks like there is a single node running into "rx".
This node gets inputs from several others.
So it looks like we need to know when all those others will be "on" at the same time.
I spent some time trying to figure this out theoretically, but I don't think that is
    going to be too fruitful.
Maybe it's possible, but I don't know if I have the time or knowledge to do that.
Instead I'm going to assume that all the inputs upstream of that one
    accumulator node are cyclic.
I run the input long enough to find all their cycles, then the answer is LCM.
"""

import logging
from collections.abc import Iterable
from collections import Counter, deque
from enum import Enum
from math import lcm
from typing import Any

PART_ONE_EXAMPLE = """\
broadcaster -> a
%a -> inv, con
&inv -> b
%b -> con
&con -> output
"""
PART_ONE_EXAMPLE_RESULT = 11687500
PART_ONE_RESULT = 1020211150
PART_TWO_EXAMPLE = """\
"""
PART_TWO_EXAMPLE_RESULT = None
PART_TWO_RESULT = None

log = logging.getLogger(__name__)

BUTTON_NAME = "button"
BROADCAST_NAME = "broadcaster"


class PulseLevel(Enum):
    Low = 0
    High = 1


PulseEvent = tuple[PulseLevel, "Module", "Module"]
PulseQueue = deque[PulseEvent]
PulseTrain = tuple[PulseEvent, ...]
ModuleState = tuple[str, Any]
NetworkState = tuple[ModuleState, int, int]


class Module:
    name: str
    downstream: list["Module"]
    pulse_queue: PulseQueue

    def __init__(self, name: str, pulse_queue: PulseQueue):
        self.name = name
        self.downstream = []
        self.pulse_queue = pulse_queue

    def establish_connection(self, upstream: "Module"):
        pass

    def send(self, pulse_level: PulseLevel):
        self.pulse_queue.extend(
            (pulse_level, self, downstream) for downstream in self.downstream
        )

    def receive(self, pulse_level: PulseLevel, source: "Module"):
        pass

    @property
    def state(self) -> ModuleState:
        return self.name, 0

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


class FlipFlop(Module):
    on: bool = False

    def receive(self, pulse_level: PulseLevel, source: Module):
        if pulse_level == PulseLevel.Low:
            self.on = not self.on
            self.send(PulseLevel.High if self.on else PulseLevel.Low)

    @property
    def state(self) -> ModuleState:
        return self.name, self.on


class Conjunction(Module):
    upstream: dict[str, PulseLevel]

    def __init__(self, name: str, pulse_queue: PulseQueue):
        super().__init__(name, pulse_queue)
        self.upstream = {}

    def establish_connection(self, upstream: "Module"):
        self.upstream[upstream.name] = PulseLevel.Low

    def receive(self, pulse_level: PulseLevel, source: Module):
        self.upstream[source.name] = pulse_level
        if self.all_high:
            self.send(PulseLevel.Low)
        else:
            self.send(PulseLevel.High)

    @property
    def all_high(self):
        return all(value == PulseLevel.High for value in self.upstream.values())

    @property
    def state(self) -> ModuleState:
        return self.name, tuple(self.upstream.values())


class Broadcast(Module):
    def receive(self, pulse_level: PulseLevel, source: Module):
        self.send(pulse_level)


def connect_modules(source: Module, destination: Module):
    source.downstream.append(destination)
    destination.establish_connection(source)


def total(num_low: int, num_high: int):
    return num_low * num_high


class Network:
    button: Module
    modules: dict[str, Module]
    pulse_queue: PulseQueue

    state_memory: list[NetworkState]
    cycle_start_idx: int | None = None
    cycle_len: int | None = None

    def __init__(self, lines: Iterable[str]):
        self.pulse_queue = deque()
        self.modules = {}

        names = []
        connections = {}
        for line in lines:
            name, connections_str = line.split(" -> ")
            short_name = name[1:] if name[0] in "%&" else name
            names.append(name)
            connections[short_name] = connections_str.split(", ")

        self._add_modules(names)
        for source, dests in connections.items():
            for dest in dests:
                self._connect_modules_by_name(source, dest)

        self._add_button()

        self.state_memory = []
        self.record_state()

    def _add_modules(self, names: list[str]):
        for name in names:
            if name[0] == "%":
                short_name = name[1:]
                self.modules[short_name] = FlipFlop(short_name, self.pulse_queue)
            elif name[0] == "&":
                short_name = name[1:]
                self.modules[short_name] = Conjunction(short_name, self.pulse_queue)
            elif name == BROADCAST_NAME:
                self.modules[name] = Broadcast(name, self.pulse_queue)
            else:
                self.modules[name] = Module(name, self.pulse_queue)

    def _connect_modules_by_name(self, source: str, destination: str):
        source_module = self.modules[source]
        if destination not in self.modules:
            self.modules[destination] = Module(destination, self.pulse_queue)
        dest_module = self.modules[destination]
        connect_modules(source_module, dest_module)

    def _add_button(self):
        self.button = Module(BUTTON_NAME, self.pulse_queue)
        self.modules[BUTTON_NAME] = self.button
        connect_modules(self.button, self.modules[BROADCAST_NAME])

    def push_button(self):
        self.button.send(PulseLevel.Low)
        sent = []
        log.debug("Processing pulses")
        while self.pulse_queue:
            pulse = self.pulse_queue.popleft()
            pulse_level, source, destination = pulse
            sent.append(pulse)
            log.debug(
                f" + {source.name} -{pulse_level.name.lower()}-> " f"{destination.name}"
            )
            destination.receive(pulse_level, source)
        log.debug("Done processing pulses")
        self.record_state(tuple(sent))

    def push_button_n_times(self, num_times: int = 1):
        for push_counter in range(num_times):
            self.push_button()

            if self.found_state_cycle():
                # We can fast-forward our counts to where they need to be
                # init_state = self.state_memory[0]
                cycle_end_idx = self.cycle_start_idx + self.cycle_len
                num_cycles_to_target_idx = (
                    num_times - self.cycle_start_idx
                ) // self.cycle_len
                log.debug(
                    f"Target {num_times} = "
                    f"{num_cycles_to_target_idx}*{self.cycle_len} + "
                    f"{self.cycle_start_idx}"
                )

                cycle_start_low, cycle_start_high = self.state_memory[
                    self.cycle_start_idx
                ][-2:]
                log.debug(
                    f"At cycle start {self.cycle_start_idx} we had sent "
                    f"{cycle_start_low} low and {cycle_start_high} high"
                )

                cycle_end_low, cycle_end_high = self.state_memory[cycle_end_idx][-2:]
                log.debug(
                    f"At cycle end {cycle_end_idx} we had sent "
                    f"{cycle_end_low} low and {cycle_end_high} high"
                )

                num_low_per_cycle = cycle_end_low - cycle_start_low
                num_high_per_cycle = cycle_end_high - cycle_start_high
                log.debug(
                    f"{num_low_per_cycle} low/cycle, {num_high_per_cycle} high/cycle"
                )

                target_low = (
                    cycle_start_low + num_low_per_cycle * num_cycles_to_target_idx
                )
                target_high = (
                    cycle_start_high + num_high_per_cycle * num_cycles_to_target_idx
                )
                log.debug(
                    f"At target {num_times} we will have sent "
                    f"{num_low_per_cycle}*{num_cycles_to_target_idx} + "
                    f"{cycle_start_low} = {target_low} low pulses"
                )
                log.debug(
                    f"At target {num_times} we will have sent {num_high_per_cycle}"
                    f"*{num_cycles_to_target_idx} + {cycle_start_high}"
                    f" = {target_high} high pulses"
                )
                fake_final_state = (tuple(), target_low, target_high)
                self.state_memory.append(fake_final_state)
                break

    @property
    def total(self):
        last_state = self.state_memory[-1]
        return total(last_state[-2], last_state[-1])

    @property
    def state(self) -> NetworkState:
        return tuple(module.state for module in self.modules.values())

    def record_state(self, sent: PulseTrain | None = None):
        sent = sent or tuple()
        sent_counts = Counter(pulse[0] for pulse in sent)
        sent_low, sent_high = sent_counts[PulseLevel.Low], sent_counts[PulseLevel.High]
        if self.state_memory:
            last_state = self.state_memory[-1]
            total_low, total_high = last_state[-2:]
        else:
            total_low, total_high = 0, 0
        state = (self.state, total_low + sent_low, total_high + sent_high)
        # log.debug(f"Recording {state}")
        self.state_memory.append(state)

    def found_state_cycle(self) -> bool:
        last_pulses, last_ltotal, last_htotal = self.state_memory[-1]
        for state_idx, (pulses, ltotal, htotal) in enumerate(self.state_memory[:-1]):
            if last_pulses == pulses:
                last_state_idx = len(self.state_memory) - 1
                log.debug(" ~~~ Found state cycle! ~~~")
                log.debug(f" ++ State {state_idx} ({pulses}, {ltotal}, {htotal})")
                log.debug(
                    f" ++ State {last_state_idx} "
                    f"({last_pulses} {last_ltotal} {last_htotal})"
                )
                self.cycle_start_idx = state_idx
                self.cycle_len = last_state_idx - state_idx
                log.debug(f" + cycle len {last_state_idx}-{state_idx}={self.cycle_len}")
                return True

        return False

    def find_upstream(self, node_name: str) -> list[Module]:
        return [
            module
            for name, module in self.modules.items()
            if any(downstream.name == node_name for downstream in module.downstream)
        ]

    def find_cycle_lengths(
        self, nodes: list[Module], limit: int = 4096
    ) -> dict[str, int]:
        cycle_lengths = {node.name: -1 for node in nodes}
        for presses in range(limit):
            self.push_button()
            for node in nodes:
                if cycle_lengths[node.name] > -1:
                    continue
                if (
                    isinstance(node, FlipFlop)
                    and node.on
                    or isinstance(node, Conjunction)
                    and not node.all_high
                ):
                    cycle_lengths[node.name] = presses

            if all(val > -1 for val in cycle_lengths.values()):
                break

        return cycle_lengths


def part_one(lines: Iterable[str]) -> int:
    network = Network(lines)
    network.push_button_n_times(1000)
    return network.total


def part_two(lines: Iterable[str]) -> int:
    network = Network(lines)
    accumulators = network.find_upstream("rx")
    assert len(accumulators) == 1
    accumulator = accumulators[0]
    log.debug(f"Found accumulator node {accumulator}")
    accumulator_inputs = network.find_upstream(accumulator.name)
    log.debug(f"Found inputs to accumulator {accumulator_inputs}")

    cycle_lengths = network.find_cycle_lengths(accumulator_inputs, 2**13)
    # print(cycle_lengths)
    return lcm(*cycle_lengths.values())
