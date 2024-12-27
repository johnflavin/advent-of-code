#!/usr/bin/env python
"""
PART 1
Given batches of key: value pairs
Count how many have a special set of keys.

PART 2
Add validation on the values
"""
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
ecl:gry pid:860033327 eyr:2020 hcl:#fffffd
byr:1937 iyr:2017 cid:147 hgt:183cm

iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884
hcl:#cfa07d byr:1929

hcl:#ae17e1 iyr:2013
eyr:2024
ecl:brn pid:760753108 byr:1931
hgt:179cm

hcl:#cfa07d eyr:2025 pid:166559648
iyr:2011 ecl:brn hgt:59in
"""
PART_ONE_EXAMPLE_RESULT = 2
PART_ONE_RESULT = 226
PART_TWO_EXAMPLE = """\
eyr:1972 cid:100
hcl:#18171d ecl:amb hgt:170 pid:186cm iyr:2018 byr:1926

iyr:2019
hcl:#602927 eyr:1967 hgt:170cm
ecl:grn pid:012533040 byr:1946

hcl:dab227 iyr:2012
ecl:brn hgt:182cm pid:021572410 eyr:2020 byr:1992 cid:277

hgt:59cm ecl:zzz
eyr:2038 hcl:74454a iyr:2023
pid:3556412378 byr:2007

pid:087499704 hgt:74in ecl:grn iyr:2012 eyr:2030 byr:1980
hcl:#623a2f

eyr:2029 ecl:blu cid:129 byr:1989
iyr:2014 pid:896056539 hcl:#a97842 hgt:165cm

hcl:#888785
hgt:164cm byr:2001 iyr:2015 cid:88
pid:545766238 ecl:hzl
eyr:2022

iyr:2010 hgt:158cm hcl:#b6652a ecl:blu byr:1944 eyr:2021 pid:093154719
"""
PART_TWO_EXAMPLE_RESULT = 4
PART_TWO_RESULT = 160

log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


def parse(lines: Iterable[str]) -> list[dict[str, str]]:
    ds = []
    d = {}
    for line in lines:
        if line == "":
            ds.append(d)
            d = {}
            continue
        d.update(tuple(kv.split(":")) for kv in line.split(" "))
    ds.append(d)
    return ds


def part_one(lines: Iterable[str]) -> int:
    passports = parse(lines)
    min_keys = {"byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"}
    max_keys = {*min_keys, "cid"}

    return sum(min_keys <= p.keys() <= max_keys for p in passports)


def part_two(lines: Iterable[str]) -> int:
    digits = set("0123456789")
    hexdigits = digits | set("abcdef")
    eyecolors = {"amb", "blu", "brn", "gry", "grn", "hzl", "oth"}
    validations = {
        "byr": lambda v: 1920 <= int(v) <= 2002,
        "iyr": lambda v: 2010 <= int(v) <= 2020,
        "eyr": lambda v: 2020 <= int(v) <= 2030,
        "hgt": lambda v: ((v[-2:] == "cm") and (150 <= int(v[:-2]) <= 193))
        or ((v[-2:] == "in") and (59 <= int(v[:-2]) <= 76)),
        "hcl": lambda v: v[0] == "#" and set(v[1:]) <= hexdigits,
        "ecl": lambda v: v in eyecolors,
        "pid": lambda v: len(v) == 9 and set(v) <= digits,
        "cid": lambda v: True,
    }

    def is_valid(key: str, value: str) -> bool:
        result = validations[key](value)
        log.debug("%s: %s %svalid", key, value, "" if result else "in")
        return result

    passports = parse(lines)
    min_keys = {"byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"}
    max_keys = {*min_keys, "cid"}
    return sum(
        min_keys <= p.keys() <= max_keys and all(is_valid(k, v) for k, v in p.items())
        for p in passports
    )
