#!/usr/bin/env python
"""
PART 1
Given lists of ingredients (random chars) and allergens.
Each allergen corresponds with some ingredient.
Allergens are not always listed when their ingredient is present.
Count ingredients that cannot possibly be an allergen.

PART 2
Identify which ingredient contains which allergen.
Output a comma-separted string of the ingredients sorted by allergen name.
"""
import itertools
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
mxmxvkd kfcds sqjhc nhms (contains dairy, fish)
trh fvjkl sbzzf mxmxvkd (contains dairy)
sqjhc fvjkl (contains soy)
sqjhc mxmxvkd sbzzf (contains fish)
"""
PART_ONE_EXAMPLE_RESULT = 5
PART_ONE_RESULT = 2493
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = "mxmxvkd,sqjhc,fvjkl"
PART_TWO_RESULT = "kqv,jxx,zzt,dklgl,pmvfzk,tsnkknk,qdlpbt,tlgrhdh"

log = logging.getLogger(__name__)


def parse(line: str) -> tuple[set[str], set[str]]:
    ingredients_str, allergens_str = line[:-1].split(" (contains ")
    return set(ingredients_str.split()), set(allergens_str.split(", "))


def find_allergen_possibilities(
    ingredients_allergens: Iterable[tuple[set[str], set[str]]]
) -> tuple[set[str], dict[str, set[str]]]:
    all_ingredients, all_allergens = [
        set().union(*s) for s in zip(*ingredients_allergens)
    ]
    allergen_possibilities = {}
    for allergen in all_allergens:
        possible_ingredients = set(all_ingredients)
        for ingrs, allers in ingredients_allergens:
            if allergen in allers:
                possible_ingredients &= ingrs

        allergen_possibilities[allergen] = possible_ingredients

        log.debug(
            "allergen %s - possible ingredients %s", allergen, possible_ingredients
        )

    return all_ingredients, allergen_possibilities


def part_one(lines: Iterable[str]) -> int:
    ingredients_allergens = [parse(line) for line in lines]

    all_ingredients, allergen_possibilities = find_allergen_possibilities(
        ingredients_allergens
    )

    cannot_be_an_allergen = all_ingredients - set(
        itertools.chain.from_iterable(v for v in allergen_possibilities.values())
    )
    log.debug("cannot be an allergen %s", cannot_be_an_allergen)

    return sum(
        1
        for ingrs, _ in ingredients_allergens
        for ingr in ingrs
        if ingr in cannot_be_an_allergen
    )


def part_two(lines: Iterable[str]) -> str:
    ingredients_allergens = [parse(line) for line in lines]

    _, allergen_possibilities = find_allergen_possibilities(ingredients_allergens)

    known_allergens = {}
    while allergen_possibilities:
        for a, aposs in allergen_possibilities.items():
            if len(aposs) == 1:
                break
        del allergen_possibilities[a]
        known_ingr = aposs.pop()
        known_allergens[a] = known_ingr
        for b, bposs in allergen_possibilities.items():
            bposs.discard(known_ingr)

    return ",".join(ingr for _, ingr in sorted(known_allergens.items()))
