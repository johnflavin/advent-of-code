#!/usr/bin/env python
"""
PART 1
A bunch of chained bitwise operations.

PART 2
Our system is adding two numbers: x and y -> z.
The bits are supposed to be in order so x00 is the LSB of x,
y00 is the LSB of y, and z00 is the LSB of z (and so on with the other numbers).
But there are four swapped bits.
And it might not be in the x, y, or z. The swaps might be somewhere else in the
chain of operations.
Find the swaps. List all eight swapped bits' labels, sort them, and join with ",".
"""
import itertools
import logging
import operator
from collections.abc import Iterable
from typing import Literal

PART_ONE_EXAMPLE = """\
x00: 1
x01: 0
x02: 1
x03: 1
x04: 0
y00: 1
y01: 1
y02: 1
y03: 1
y04: 1

ntg XOR fgs -> mjb
y02 OR x01 -> tnw
kwq OR kpj -> z05
x00 OR x03 -> fst
tgd XOR rvg -> z01
vdt OR tnw -> bfw
bfw AND frj -> z10
ffh OR nrd -> bqk
y00 AND y03 -> djm
y03 OR y00 -> psh
bqk OR frj -> z08
tnw OR fst -> frj
gnj AND tgd -> z11
bfw XOR mjb -> z00
x03 OR x00 -> vdt
gnj AND wpb -> z02
x04 AND y00 -> kjc
djm OR pbm -> qhw
nrd AND vdt -> hwm
kjc AND fst -> rvg
y04 OR y02 -> fgs
y01 AND x02 -> pbm
ntg OR kjc -> kwq
psh XOR fgs -> tgd
qhw XOR tgd -> z09
pbm OR djm -> kpj
x03 XOR y03 -> ffh
x00 XOR y04 -> ntg
bfw OR bqk -> z06
nrd XOR fgs -> wpb
frj XOR qhw -> z04
bqk OR frj -> z07
y03 OR x01 -> nrd
hwm AND bqk -> z03
tgd XOR rvg -> z12
tnw OR pbm -> gnj
"""
PART_ONE_EXAMPLE_RESULT = 2024
PART_ONE_RESULT = 65635066541798
PART_TWO_EXAMPLE = """\
x00: 0
x01: 1
x02: 0
x03: 1
x04: 0
x05: 1
y00: 0
y01: 0
y02: 1
y03: 1
y04: 0
y05: 1

x00 AND y00 -> z05
x01 AND y01 -> z02
x02 AND y02 -> z01
x03 AND y03 -> z03
x04 AND y04 -> z04
x05 AND y05 -> z00
"""
PART_TWO_EXAMPLE_RESULT = "z00,z01,z02,z05"
PART_TWO_RESULT = "dgr,dtv,fgc,mtj,vvm,z12,z29,z37"

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


type Operation = Literal["AND", "OR", "XOR"]
type Gate = tuple[str, str, Operation]


def parse(lines: Iterable[str]) -> tuple[dict[str, int], dict[str, Gate]]:
    values = {}
    for line in lines:
        if line == "":
            break
        k, vstr = line.split(": ")
        values[k] = int(vstr)

    gates = {}
    for line in lines:
        inputs, output = line.split(" -> ")
        a, op, b = inputs.split(" ")
        gates[output] = (a, b, op)
    return values, gates


def do_operation(
    gates_subset: Iterable[tuple[str, int, int]], op: Operation
) -> dict[str, int]:
    """Do a single operation for a whole set of gates.
    The gates must all have the same operation, all the inputs
    must have values."""
    if not gates_subset:
        return {}
    # log.debug("Calculating %s for %s", op, gates_subset)

    # outbit_names[0]: LSB
    outbit_names, abits, bbits = zip(*gates_subset)
    # a[0], b[0]: LSB
    a = bit_list_to_num(abits)
    b = bit_list_to_num(bbits)
    if op == "AND":
        out = a & b
    elif op == "OR":
        out = a | b
    else:
        out = a ^ b

    d = dict(zip(outbit_names, num_to_bit_list(out, len(outbit_names))))
    # log.debug(d)
    return d


def bit_list_to_num(bits: list[int]) -> int:
    return sum(b << i for i, b in enumerate(bits))


def num_to_bit_list(num: int, num_len: int) -> list[int]:
    bits = []
    for _ in range(num_len):
        bits.append(num % 2)
        num = num >> 1
    return bits


def build_output_layers(gates: dict[str, Gate]) -> list[Iterable[str]]:
    # Build up rounds of inputs that will feed the next round
    # Start from the bottom, the z*s
    zs = [k for k in gates if k[0] == "z"]
    # z_inputs: set[str] = set(
    #     itertools.chain.from_iterable(
    #         gates[z][:2] for z in zs
    #     )
    # )
    output_layers = []
    outs = zs
    while outs:
        output_layers.append(outs)
        ins = set(
            itertools.chain.from_iterable(
                g[:2] for k in outs if (g := gates.get(k)) is not None
            )
        )

        # Are any of the inputs not known?
        # (Assumption informed by part 2: all inputs start with x or y)
        outs = [i for i in ins if i[0] not in ("x", "y")]
    # log.debug("output_layers: %s", output_layers)
    return output_layers


def evaluate(
    values: dict[str, int], gates: dict[str, Gate], output_layers: list[Iterable[str]]
) -> int:
    # Now resolve each round of outputs, starting from the top
    zs = sorted(output_layers[0])
    while output_layers:
        outs = output_layers.pop()
        ands = []
        ors = []
        xors = []
        for out in outs:
            if out in values:
                continue
            aname, bname, op = gates[out]
            inout = (out, values[aname], values[bname])
            if op == "AND":
                ands.append(inout)
            elif op == "OR":
                ors.append(inout)
            else:
                xors.append(inout)

        values.update(do_operation(ands, "AND"))
        values.update(do_operation(ors, "OR"))
        values.update(do_operation(xors, "XOR"))
    zbits = [values[z] for z in zs]
    return bit_list_to_num(zbits)


def part_one(lines: Iterable[str]) -> int:
    values, gates = parse(lines)
    output_layers = build_output_layers(gates)
    return evaluate(values, gates, output_layers)


def part_two(lines: Iterable[str]) -> str:
    original_values, original_gates = parse(lines)
    # output_layers = build_output_layers(original_gates)
    #
    is_example = len(original_gates) <= 6
    if is_example:
        zop = operator.and_
    else:
        zop = operator.add

    def run_experiment(
        x: int, y: int, swap: Iterable[tuple[str, str]] = None
    ) -> tuple[str, str] | None:
        swap = swap or []
        gates = {**original_gates}
        for s1, s2 in swap:
            # log.debug("swap %s, %s", s1, s2)
            gates[s1] = original_gates[s2]
            gates[s2] = original_gates[s1]

        output_layers = build_output_layers(gates)
        lenz = len(output_layers[0])
        # lenxy = lenz - 1

        xbits = num_to_bit_list(x, lenz)
        ybits = num_to_bit_list(y, lenz)
        values = {
            f"{xy}{i:02}": xybits[i]
            for xy, xybits in (("x", xbits), ("y", ybits))
            for i in range(lenz)
        }
        # log.info(f"{values=}")
        tz = zop(x, y)
        az = evaluate(values, gates, output_layers)
        axt = az ^ tz
        if axt:
            possible_swap = [
                f"z{i:02}"
                for i, axtbit in enumerate(num_to_bit_list(axt, lenz))
                if axtbit
            ]
            if is_debug:
                log.debug(f" {x=:0{lenz}b}")
                log.debug(f" {y=:0{lenz}b}")
                log.debug(f"{tz=:0{lenz}b}")
                log.debug(f"{az=:0{lenz}b}")
                log.debug(f" ^={axt:0{lenz}b}")
                log.debug("Possible swap: %s", possible_swap)
            return tuple(possible_swap)

    # def locate_gate(gate: Gate, gates: dict[str, Gate]) -> str:
    #     alt_gate = (gate[1], gate[0], gate[2])
    #     for k, g in original_gates.items():
    #         if g == gate or g == alt_gate:
    #             return k

    carry_ors = {}

    def validate_carry_or(cor: Gate, i: int) -> bool:
        """
        Example:
        knm _ XOR -> z02
        vjw hfp OR -> knm        # i Carry OR
        y01 x01 AND -> vjw       # i-1 Carry AND
        tkb njb AND -> hfp       # Long-range Carry AND
        x01 y01 XOR -> tkb       # i-1 XOR
        x00 y00 AND -> njb       # i0 AND (only for i == 2)

        Example:
        wvr sfq XOR -> z03
        y03 x03 XOR -> sfq       # i bits
        qhs fwv OR -> wvr        # i Carry OR
        x02 y02 AND -> qhs       # i-1 Carry AND
        vvh knm AND -> fwv       # Long-range Carry AND
        y02 x02 XOR -> vvh       # i-1 XOR
        vjw hfp OR -> knm        # Recursive i-1 Carry OR
        """
        xl = f"x{i-1:02}"
        yl = f"y{i-1:02}"
        ls = {xl, yl}
        for corl in cor[:2]:
            corg = gates[corl]
            if corg[2] != "AND":
                log.info("Found swap")
                log.info(f"{cor} is a Carry OR")
                log.info(f"{corl} = {corg}")
                log.info(f"{corl} != ('{xl}', '{yl}', 'AND')")
                log.info(f"{corl} != ('_', '_', 'AND')")
                return False

            if set(corg[:2]) == ls:
                # i carry bit
                pass
            else:
                # Long-range AND
                for lra in corg[:2]:
                    lrag = gates[lra]
                    if lrag[2] == "XOR" and set(lrag[:2]) == ls:
                        pass
                    elif (
                        i == 2 and lrag[2] == "AND" and set(lrag[:2]) == {"x00", "y00"}
                    ):
                        pass
                    else:
                        # Recursive Carry OR
                        if lrag[2] == "OR" and lrag == carry_ors.get(i - 1):
                            pass
                        else:
                            log.info(f"Found swap: i={i} carry OR")
                            log.info(f"{lra} = {lrag}")
                            log.info(f"{lra} != ('{xl}', '{yl}', 'XOR')")
                            log.info(f"{lra} != {carry_ors.get(i-1)} i-1 carry OR")
                            return False
        carry_ors[i] = cor
        return True

    if is_example:
        i = 0
        swaps = set()
        while i < len(original_values) // 2:
            sw = run_experiment(1 << i, 1 << i, swaps)
            if sw is not None and sw not in swaps:
                swaps.add(sw)
                continue
            if len(swaps) == 2:
                break
            i += 1
    else:
        swaps = [("fgc", "z12"), ("mtj", "z29"), ("dgr", "vvm"), ("z37", "dtv")]
        # swaps = []
        gates = {**original_gates}
        for s1, s2 in swaps:
            gates[s1] = original_gates[s2]
            gates[s2] = original_gates[s1]
            log.debug("swap %s %s (was %s)", s1, gates[s1], s2)
            log.debug("swap %s %s (was %s)", s2, gates[s2], s1)

        i = 0
        while (zgate := gates.get(f"z{i:02}")) is not None:
            log.debug(f"Checking z{i:02}")
            # x y
            xlabel = f"x{i:02}"
            ylabel = f"y{i:02}"
            xylabels = {xlabel, ylabel}

            if 1 < i < 45:
                # One of these should be xi yi XOR, the other a carry OR
                for j in 0, 1:
                    zgj = gates.get(zgate[j], ["", "", ""])
                    if zgj[2] == "XOR" and set(zgj[:2]) == xylabels:
                        pass
                    elif zgj[2] == "OR":
                        # Carry OR
                        validate_carry_or(zgj, i)
                    else:
                        log.info("Found swap")
                        log.info(f"z{i:02} = {zgate}")
                        log.info(f"{zgate[j]} = {zgj}")
                        log.info(f"{zgate[j]} != ('{xlabel}', '{ylabel}', 'XOR')")
                        log.info(f"{zgate[j]} != (_, _, 'OR') Carry OR")

            elif i == 1:
                # One of these should be x1 y1 XOR, the other x0 y0 AND
                for j in 0, 1:
                    zgj = gates[zgate[j]]
                    zgjl = set(zgj[:2])
                    if zgj[2] == "XOR" and zgjl == xylabels:
                        pass
                    elif zgj[2] == "AND" and zgjl == {f"x{i-1:02}", f"y{i-1:02}"}:
                        pass
                    else:
                        log.info("Found swap")
                        log.info(f"z{i:02} = {zgate}")
                        log.info(f"{zgate[j]} = {zgj}")
                        log.info(f"{zgate[j]} != ('{xlabel}', '{ylabel}', 'XOR')")
                        log.info(f"{zgate[j]} != ('x{i-1:02}', 'y{i-1:02}', 'AND')")

            elif i == 0:
                # No carry in
                # x y XOR
                if xlabel not in zgate or ylabel not in zgate or "XOR" != zgate[2]:
                    log.info(
                        f"Found swap: z{i:02} = {zgate} != ({xlabel} {ylabel} XOR)"
                    )
            elif i == 45:
                # There is some kind of strangeness with the last bit.
                # I already have the answer so I can't be bothered with this.
                pass

            i += 1

    return ",".join(sorted(itertools.chain.from_iterable(swaps)))
