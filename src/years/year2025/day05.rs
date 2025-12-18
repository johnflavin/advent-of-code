// use std::ops::Add;
use crate::range::{union, Range};
use crate::solver::Solver;
use anyhow::Result;
use log::debug;

pub struct Day05;

impl Solver for Day05 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        5
    }

    fn part1_example(&self) -> &str {
        "3-5
10-14
16-20
12-18

1
5
8
11
17
32"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("3")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("14")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("601")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("367899984917516")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        let (ranges, test_values) = parse(_input);
        let total = test_values.iter().fold(0, |acc, x| {
            acc + (if ranges.iter().any(|r| r.contains(x)) {
                1
            } else {
                0
            })
        });
        Ok(total.to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        let (ranges, _) = parse(_input);
        let total = ranges.iter().fold(0, |acc, range| acc + range.len());
        Ok(total.to_string())
    }
}

fn parse(_input: &str) -> (Vec<Range<u64>>, Vec<u64>) {
    let mut ranges = Vec::new();
    let mut test_values = Vec::new();

    let mut seen_a_blank_line = false;
    for line in _input.trim().lines() {
        if !seen_a_blank_line && line.is_empty() {
            seen_a_blank_line = true;
            continue;
        } else if !seen_a_blank_line {
            let (left_s, right_s) = line.split_once("-").unwrap();
            ranges.push(Range::new(
                left_s.parse().unwrap(),
                right_s.parse().unwrap(),
            ));
        } else {
            test_values.push(line.parse().unwrap());
        }
    }

    debug!("ranges: {:?}", ranges);

    let disjoint_ranges = union(ranges);

    debug!("disjoint ranges: {:?}", disjoint_ranges);
    debug!("test_values: {:?}", test_values);

    (disjoint_ranges, test_values)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_part1_example() {
        let day = Day05;
        if let Some(expected) = day.part1_example_result() {
            let result = day.part1(day.part1_example()).unwrap();
            assert_eq!(result, expected);
        }
    }

    #[test]
    fn test_part2_example() {
        let day = Day05;
        if let Some(expected) = day.part2_example_result() {
            let result = day.part2(day.part2_example()).unwrap();
            assert_eq!(result, expected);
        }
    }
}
