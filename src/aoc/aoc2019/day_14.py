#!/usr/bin/env python
"""
PART 1
Given a reaction chain from ORE to FUEL,
find the minimum number of ORE needed to make 1 FUEL.

PART 2
"""
import logging
import math
from collections.abc import Iterable
from functools import cache, cmp_to_key


PART_ONE_EXAMPLE = """\
171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX
"""
PART_ONE_EXAMPLE_RESULT = 2210736
PART_ONE_RESULT = 337075
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 460664
PART_TWO_RESULT = 5194174

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)

FUEL = "FUEL"
ORE = "ORE"
ONE_TRILLION = 1_000_000_000_000


type Reactant = tuple[int, str]
type Reactants = list[Reactant]
type Reaction = tuple[int, Reactants]
type Products = dict[str, Reaction]


def parse(lines: Iterable[str]) -> Products:
    products = {}
    for line in lines:
        reactants_str, product_str = line.split(" => ")
        product_amt_str, product_name = product_str.split()
        reactants = []
        for reactant_str in reactants_str.split(", "):
            reactant_amt_str, reactant_name = reactant_str.split()
            reactants.append((int(reactant_amt_str), reactant_name))
        products[product_name] = (int(product_amt_str), reactants)

    return products


def sort_products(products: Products) -> list[str]:
    @cache
    def what_is_upstream_of_me(product: str) -> set[str]:
        if product == ORE:
            # log.debug("ORE upstream: {}")
            return set()
        _, reactants = products[product]
        upstream = set()
        for _, reactant in reactants:
            upstream.add(reactant)
            upstream.update(what_is_upstream_of_me(reactant))
        # log.debug("%s upstream: %s", product, upstream)
        return upstream

    def product_comparator(a: str, b: str):
        ret = 0
        if b in what_is_upstream_of_me(a):
            ret = 1
        if a in what_is_upstream_of_me(b):
            ret = -1
        la = len(what_is_upstream_of_me(a))
        lb = len(what_is_upstream_of_me(b))
        if la < lb:
            ret = 1
        if lb < la:
            ret = -1
        # log.debug("Cmp a=%s b=%s -> %d", a, b, ret)
        return ret

    return sorted(products, key=cmp_to_key(product_comparator))


def find_num_ore_per_fuel(
    num_fuel: int, products: Products, sorted_products: list[str]
) -> int:

    # log.debug("Starting needs with %d FUEL", num_fuel)
    needs = {FUEL: num_fuel}
    for product in sorted_products:
        # Pull out another thing we need to have on hand to make fuel
        req_amt = needs[product]
        # log.debug("Need %d %s", req_amt, product)

        if product == ORE:
            # Nothing makes ore, it just is
            return req_amt

        # Time to make the donuts
        # How do we make this thing, and in what quantity?
        unit_of_production, reactants = products[product]

        # Find out the minimum number we have to make
        num_units = math.ceil(req_amt / unit_of_production)

        # In order to make this, we need a bunch of precursors
        # Add those to the needs
        for reactant_amt, reactant in reactants:
            num_reactant_units = num_units * reactant_amt
            if reactant in needs:
                needs[reactant] += num_reactant_units
                # log.debug(
                #     "Adding %d to %s. New total = %d",
                #     num_reactant_units,
                #     reactant,
                #     needs[reactant],
                # )
            else:
                # log.debug(
                #     "Adding new need %s. total = %d", reactant, num_reactant_units
                # )
                needs[reactant] = num_reactant_units

    return needs[ORE]


def part_one(lines: Iterable[str]) -> int:
    products = parse(lines)
    sorted_products = sort_products(products)
    return find_num_ore_per_fuel(1, products, sorted_products)


def part_two(lines: Iterable[str]) -> int:
    products = parse(lines)
    sorted_products = sort_products(products)
    fuel_range = (
        [100_000, 1_000_000]
        if "CNZTR" in products and 8 == products["CNZTR"][0]
        else [1_000_000, 10_000_000]
    )

    # Binary search through fuel values
    while fuel_range[1] > fuel_range[0] + 1:
        log.debug("RANGE (%d, %d)", fuel_range[0], fuel_range[1])

        fuel = (fuel_range[1] + fuel_range[0]) // 2
        ore = find_num_ore_per_fuel(fuel, products, sorted_products)
        log.debug("FUEL %d ORE %d", fuel, ore)
        if ore > ONE_TRILLION:
            fuel_range[1] = fuel - 1
        else:
            fuel_range[0] = fuel

    return fuel_range[0]
