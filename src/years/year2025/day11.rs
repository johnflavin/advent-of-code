use crate::solver::{Part, Solver};
use anyhow::Result;
use log::debug;
use std::collections::HashMap;

pub struct Day11;

impl Solver for Day11 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        11
    }

    fn part1_example(&self) -> &str {
        "\
aaa: you hhh
you: bbb ccc
bbb: ddd eee
ccc: ddd eee fff
ddd: ggg
eee: out
fff: out
ggg: out
hhh: ccc fff iii
iii: out"
    }

    fn part2_example(&self) -> &str {
        "\
svr: aaa bbb
aaa: fft
fft: ccc
bbb: tty
tty: ccc
ccc: ddd eee
ddd: hub
hub: fff
eee: dac
dac: fff
fff: ggg hhh
ggg: out
hhh: out"
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("5")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("2")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("649")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("458948453421420")
    }

    fn part1(&self, input: &str) -> Result<String> {
        Ok(Self::solve(input, Part::One).to_string())
    }

    fn part2(&self, input: &str) -> Result<String> {
        Ok(Self::solve(input, Part::Two).to_string())
    }
}

impl Day11 {
    fn parse(input: &str) -> HashMap<&str, Vec<&str>> {
        debug!("Parsing input");
        input
            .trim()
            .lines()
            .map(|line| {
                debug!("{}", line);
                let (source, rest) = line.trim().split_once(": ").unwrap();
                (source, rest.split_whitespace().collect::<Vec<_>>())
            })
            .collect::<HashMap<_, _>>()
    }

    fn solve(input: &str, part: Part) -> usize {
        let source_dest_map = Self::parse(input);

        let first_element = match part {
            Part::One => "you",
            Part::Two => "svr",
        };
        Self::count_paths(
            first_element,
            part,
            false,
            false,
            &source_dest_map,
            &mut HashMap::new(),
        )
    }

    fn count_paths<'a>(
        node: &'a str,
        part: Part,
        seen_fft: bool,
        seen_dac: bool,
        graph: &HashMap<&str, Vec<&'a str>>,
        cache: &mut HashMap<(&'a str, bool, bool), usize>,
    ) -> usize {
        if node == "out" {
            return if part == Part::One || seen_fft && seen_dac {
                1
            } else {
                0
            };
        }

        let key = (
            node,
            part == Part::One || seen_fft,
            part == Part::One || seen_dac,
        );
        if let Some(&result) = cache.get(&key) {
            return result;
        }

        let new_fft = part == Part::One || seen_fft || node == "fft";
        let new_dac = part == Part::One || seen_dac || node == "dac";

        let result = graph
            .get(node)
            .map(|children| {
                children.iter().fold(0usize, |acc, &child| {
                    acc + Self::count_paths(child, part, new_fft, new_dac, graph, cache)
                })
            })
            .unwrap_or(0);

        cache.insert(key, result);
        result
    }
}

crate::solver_tests!(Day11);
