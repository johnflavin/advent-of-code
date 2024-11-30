import argparse
import logging
import sys

from aoc.run import run_puzzle


def main(argv) -> int:
    parser = argparse.ArgumentParser(description="Run Advent of Code puzzle")
    parser.add_argument(
        "--part",
        dest="parts",
        type=int,
        required=False,
        action="append",
        help="Which part of the puzzle to run",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        required=False,
        help="Datestamp of puzzle to run (default today)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args(argv)

    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    return int(not run_puzzle(args.date, args.parts))


def main_cli() -> int:
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main_cli())
