use crate::solver::{Part, Solver};
use anyhow::Result;
use log::debug;
use std::collections::{HashSet, VecDeque};
use std::ops::BitXor;

pub struct Day10;

impl Solver for Day10 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        10
    }

    fn part1_example(&self) -> &str {
        // TODO: Add example input
        "\
[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("7")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("33")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("475")
    }

    fn part2_result(&self) -> Option<&str> {
        // TODO: Add known result for part 2
        None
    }

    /**
    Pathfinding!
    We have a starting node and an ending node, and movements between nodes.
    Find the shortest path.

    Question is how to represent the node.
    A Vec<bool>? That could work.

    Shower thought: encode as a binary number. Transitions are XORs.
    */
    fn part1(&self, input: &str) -> Result<String> {
        let total = input.trim().lines().fold(0usize, |total, line| {
            let (target_vec, transition_idx_vec) = Self::parse(line, Part::One);
            let target = target_vec
                .iter()
                .fold(0usize, |s, idx| s + (1 << idx) as usize);
            let transitions = transition_idx_vec
                .iter()
                .map(|transition_idx_vec| {
                    transition_idx_vec
                        .iter()
                        .fold(0usize, |s, idx| s + (1 << idx) as usize)
                })
                .collect::<Vec<_>>();
            total + Self::solve_part1(target, &transitions)
        });
        Ok(total.to_string())
    }
    /**
    I started trying to solve this the same way as part 1 and... no.
    What I tried there is instead of treating the basis numbers as encoding binary digits,
    I made them base b digits instead, where b was 1 + the biggest number in the target set.
    That was a mistake.

    This really seems more like a linear programming problem.
    But I don't know what that means exactly or how to solve it!
    */
    fn part2(&self, input: &str) -> Result<String> {
        let total = input.trim().lines().fold(0usize, |total, line| {
            #[allow(unused)]
            let (target_vec, transition_idx_vec) = Self::parse(line, Part::Two);
            // let target = target_vec
            //     .iter()
            //     .fold(0usize, |s, idx| s + (1 << idx) as usize);
            // let transitions = transition_idx_vec
            //     .iter()
            //     .map(|transition_idx_vec| {
            //         transition_idx_vec.iter().fold(0usize, |s, idx| s + (1 << idx) as usize)
            //     })
            //     .collect::<Vec<_>>();
            // total + Self::solve_part1(target, &transitions)
            total
        });

        Ok(total.to_string())
    }
}

impl Day10 {
    fn solve_part1(target: usize, transitions: &[usize]) -> usize {
        let mut stack = VecDeque::new();
        // Stack: (current value, number of steps)
        stack.push_front((0usize, 0usize));

        let mut seen = HashSet::new();

        while let Some((current_value, num_steps)) = stack.pop_back() {
            if seen.contains(&current_value) {
                continue;
            }
            seen.insert(current_value);
            if current_value == target {
                return num_steps;
            }

            transitions.iter().for_each(|&transition| {
                stack.push_front((current_value.bitxor(transition), num_steps + 1))
            })
        }

        0
    }

    fn parse(line: &str, part: Part) -> (Vec<usize>, Vec<Vec<usize>>) {
        debug!("{}", line);
        let mut line_iter = line.trim().chars();
        // First char is a [
        line_iter.next();

        // Next batch of characters is our target
        let mut target: Vec<usize> = Vec::new();
        for (i, c) in line_iter.by_ref().enumerate() {
            match c {
                '.' => (),
                '#' => target.push(i),
                ']' => break,
                _ => panic!("Unexpected char {}", c),
            }
        }

        // Skip a space
        line_iter.next();

        let mut transition_idx_vecs = Vec::new();
        let mut this_transition_idx_vec = Vec::new();
        let mut buffer = String::new();
        for c in line_iter.by_ref() {
            match c {
                ' ' => (),
                '(' => (),
                d if d.is_ascii_digit() => buffer.push(d),
                ',' => {
                    this_transition_idx_vec.push(buffer.parse::<usize>().unwrap());
                    buffer.clear()
                }
                ')' => {
                    this_transition_idx_vec.push(buffer.parse::<usize>().unwrap());
                    transition_idx_vecs.push(this_transition_idx_vec.clone());
                    this_transition_idx_vec.clear();
                    buffer.clear();
                }
                '{' => break,
                _ => panic!("Unexpected char {}", c),
            }
            // debug!(" c {} buffer {} current {}", c, buffer, current);
        }

        // Now parse out the targets for part 2
        let target = if part == Part::Two {
            let mut part2_target = Vec::new();
            buffer.clear();

            for c in line_iter.by_ref() {
                match c {
                    d if d.is_ascii_digit() => buffer.push(d),
                    ',' => {
                        part2_target.push(buffer.parse::<usize>().unwrap());
                        buffer.clear();
                    }
                    '}' => {
                        part2_target.push(buffer.parse::<usize>().unwrap());
                        buffer.clear();
                        break;
                    }
                    _ => panic!("Unexpected char {}", c),
                }
                // debug!(" c {} buffer {} current {}", c, buffer, current);
            }
            part2_target
        } else {
            target
        };

        debug!(
            " target: {:?}, transitions: {:?}",
            target, transition_idx_vecs
        );

        (target, transition_idx_vecs)
    }
}

crate::solver_tests!(Day10, #[ignore]);
