use crate::solver::Solver;
use anyhow::Result;
use std::collections::{HashMap, HashSet};

pub struct Day07;

impl Solver for Day07 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        7
    }

    fn part1_example(&self) -> &str {
        "\
.......S.......
...............
.......^.......
...............
......^.^......
...............
.....^.^.^.....
...............
....^.^...^....
...............
...^.^...^.^...
...............
..^...^.....^..
...............
.^.^.^.^.^...^.
..............."
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("21")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("40")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("1605")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("29893386035180")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        // Split the first line and the rest separately
        let (first_line, lines) = _input.split_once("\n").unwrap();

        // Hold the beam locations in a set b.c. we don't care about duplicates
        let mut initial_beams = HashSet::new();

        // Find the S to start the beam
        initial_beams.insert(first_line.find("S").unwrap());

        // Process the lines and sum all the splits
        let (splits, _) = lines
            .lines()
            .fold((0u64, initial_beams), |(mut splits, beams), line| {
                let mut new_beams = HashSet::new();
                let bytes = line.as_bytes();

                // For each beam location, check if it gets split
                // If it does, increment the counter
                for idx in beams {
                    if bytes[idx].eq(&b'^') {
                        splits += 1;
                        new_beams.insert(idx - 1);
                        new_beams.insert(idx + 1);
                    } else {
                        new_beams.insert(idx);
                    }
                }

                (splits, new_beams)
            });
        Ok(splits.to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        // Split the first line and the rest separately
        let (first_line, lines) = _input.split_once("\n").unwrap();

        // Hold the beam locations in a set b.c. we don't care about duplicates
        let mut initial_beams = HashMap::new();

        // Find the S to start the beam
        initial_beams.insert(first_line.find("S").unwrap(), 1);

        // Process the lines and sum all the splits
        let final_beams = lines.lines().fold(initial_beams, |beams, line| {
            let mut new_beams = HashMap::new();
            let bytes = line.as_bytes();

            // For each beam location, check if it gets split
            // If it does, increment the counter
            for (idx, count) in beams {
                if bytes[idx].eq(&b'^') {
                    *new_beams.entry(idx - 1).or_insert(0) += count;
                    *new_beams.entry(idx + 1).or_insert(0) += count;
                } else {
                    *new_beams.entry(idx).or_insert(0) += count;
                }
            }

            new_beams
        });
        Ok(final_beams.values().sum::<u64>().to_string())
    }
}

crate::solver_tests!(Day07);
