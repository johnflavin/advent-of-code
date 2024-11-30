# Advent of Code

My solutions to the puzzles in [Advent of Code](https://adventofcode.com).

## How to Install
Make a virtualenv
```shell
python -m venv .venv
source .venv/bin/activate.fish  # For fish shell
```
Install the package into the virtualenv
```shell
pip install -e .
```

## How to Run
With the package installed and the venv active, use the `aoc` script.
```shell
aoc [--date YYYY-MM-DD] [--part PART] [--debug]
```
Args
- `--date YYYY-MM-DD` the date of a puzzle to run. If omitted, use today's date.
- `--part PART` can be 1 or 2. If omitted run both.
- `--debug` turn on debug logs. If omitted INFO level log messages 
  are printed with no special format
