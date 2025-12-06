#!/usr/bin/env bash
set -euo pipefail

# Script to create a new year's worth of Advent of Code puzzle stubs
# Usage: ./scripts/new_year.sh YEAR

if [ $# -ne 1 ]; then
    echo "Usage: $0 YEAR"
    echo "Example: $0 2025"
    exit 1
fi

YEAR=$1
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
YEAR_DIR="$REPO_ROOT/src/years/year$YEAR"

# Validate year is a number
if ! [[ "$YEAR" =~ ^[0-9]{4}$ ]]; then
    echo "Error: YEAR must be a 4-digit number"
    exit 1
fi

# Check if year directory already exists
if [ -d "$YEAR_DIR" ]; then
    echo "Error: Directory $YEAR_DIR already exists"
    exit 1
fi

echo "Creating Advent of Code year $YEAR..."

# Create year directory
mkdir -p "$YEAR_DIR"

# Create day template
cat > /tmp/aoc_day_template.rs << 'EOF'
use crate::solver::Solver;
use anyhow::Result;

pub struct DayXX;

impl Solver for DayXX {
    fn year(&self) -> u16 {
        YEAR
    }

    fn day(&self) -> u8 {
        XX
    }

    fn part1_example(&self) -> &str {
        // TODO: Add example input
        ""
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        // TODO: Add expected result for part 1 example
        None
    }

    fn part2_example_result(&self) -> Option<&str> {
        // TODO: Add expected result for part 2 example
        None
    }

    fn part1_result(&self) -> Option<&str> {
        // TODO: Add known result for part 1
        None
    }

    fn part2_result(&self) -> Option<&str> {
        // TODO: Add known result for part 2
        None
    }

    fn part1(&self, _input: &str) -> Result<String> {
        // TODO: Implement part 1 solution
        Ok("0".to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        // TODO: Implement part 2 solution
        Ok("0".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_part1_example() {
        let day = DayXX;
        if let Some(expected) = day.part1_example_result() {
            let result = day.part1(day.part1_example()).unwrap();
            assert_eq!(result, expected);
        }
    }

    #[test]
    fn test_part2_example() {
        let day = DayXX;
        if let Some(expected) = day.part2_example_result() {
            let result = day.part2(day.part2_example()).unwrap();
            assert_eq!(result, expected);
        }
    }
}
EOF

# Create all 25 day files with zero-padded filenames (day01.rs, day02.rs, etc.)
echo "Creating day files..."
for day_num in {1..25}; do
    # Format day with zero-padding (works on bash 3.x which doesn't support {01..25})
    day=$(printf "%02d" $day_num)
    # day_num is the integer (1-25), $day is zero-padded (01-25)
    # Files: day01.rs, Structs: Day01, day() returns: 1
    # Important: Replace DayXX first, then XX (order matters!)
    sed "s/DayXX/Day$day/g; s/XX/$day_num/g; s/YEAR/$YEAR/g" /tmp/aoc_day_template.rs > "$YEAR_DIR/day$day.rs"
done

# Create mod.rs
echo "Creating mod.rs..."
cat > "$YEAR_DIR/mod.rs" << EOF
use crate::solver::Solver;

pub mod day01;
pub mod day02;
pub mod day03;
pub mod day04;
pub mod day05;
pub mod day06;
pub mod day07;
pub mod day08;
pub mod day09;
pub mod day10;
pub mod day11;
pub mod day12;
pub mod day13;
pub mod day14;
pub mod day15;
pub mod day16;
pub mod day17;
pub mod day18;
pub mod day19;
pub mod day20;
pub mod day21;
pub mod day22;
pub mod day23;
pub mod day24;
pub mod day25;

/// Get a solver for a specific day in $YEAR
pub fn get_solver(day: u8) -> Option<Box<dyn Solver>> {
    match day {
        1 => Some(Box::new(day01::Day01)),
        2 => Some(Box::new(day02::Day02)),
        3 => Some(Box::new(day03::Day03)),
        4 => Some(Box::new(day04::Day04)),
        5 => Some(Box::new(day05::Day05)),
        6 => Some(Box::new(day06::Day06)),
        7 => Some(Box::new(day07::Day07)),
        8 => Some(Box::new(day08::Day08)),
        9 => Some(Box::new(day09::Day09)),
        10 => Some(Box::new(day10::Day10)),
        11 => Some(Box::new(day11::Day11)),
        12 => Some(Box::new(day12::Day12)),
        13 => Some(Box::new(day13::Day13)),
        14 => Some(Box::new(day14::Day14)),
        15 => Some(Box::new(day15::Day15)),
        16 => Some(Box::new(day16::Day16)),
        17 => Some(Box::new(day17::Day17)),
        18 => Some(Box::new(day18::Day18)),
        19 => Some(Box::new(day19::Day19)),
        20 => Some(Box::new(day20::Day20)),
        21 => Some(Box::new(day21::Day21)),
        22 => Some(Box::new(day22::Day22)),
        23 => Some(Box::new(day23::Day23)),
        24 => Some(Box::new(day24::Day24)),
        25 => Some(Box::new(day25::Day25)),
        _ => None,
    }
}
EOF

# Add year to years/mod.rs
YEARS_MOD="$REPO_ROOT/src/years/mod.rs"
echo "Updating $YEARS_MOD..."

# Add module declaration
if ! grep -q "^pub mod year$YEAR;" "$YEARS_MOD"; then
    # Insert after the last "pub mod year" line
    sed -i.bak "/^pub mod year/a\\
pub mod year$YEAR;" "$YEARS_MOD"
    rm -f "$YEARS_MOD.bak"
fi

# Add case to get_solver function
if ! grep -q "^[[:space:]]*$YEAR =>" "$YEARS_MOD"; then
    # Insert before the _ => None line
    sed -i.bak "/^[[:space:]]*_ => None,/i\\
        $YEAR => year$YEAR::get_solver(day)," "$YEARS_MOD"
    rm -f "$YEARS_MOD.bak"
fi

# Clean up
rm /tmp/aoc_day_template.rs

echo "✓ Created year$YEAR with 25 day stubs"
echo "✓ Updated src/years/mod.rs"
echo ""
echo "Next steps:"
echo "  1. Run 'cargo build' to verify everything compiles"
echo "  2. Start solving puzzles in src/years/year$YEAR/day01.rs"
echo "  3. Run with: cargo run -- --date $YEAR-12-01"
