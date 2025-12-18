use crate::solver::Solver;
use anyhow::Result;
use log::debug;

pub struct Day03;

impl Solver for Day03 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        3
    }

    fn part1_example(&self) -> &str {
        "987654321111111
811111111111119
234234234234278
818181911112111"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("357")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("3121910778619")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("16927")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("167384358365132")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        let lines = parse(_input);

        let num_digits = 2;

        let total = lines
            .iter()
            .fold(0, |acc, line| acc + find_max(line, num_digits));

        Ok(total.to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        let lines = parse(_input);

        let num_digits = 12;

        let total = lines
            .iter()
            .fold(0, |acc, line| acc + find_max(line, num_digits));

        Ok(total.to_string())
    }
}

fn find_max(line: &Vec<u8>, num_digits: usize) -> u64 {
    debug!("line {:?}", line);

    let mut max_indices = (0..num_digits).collect::<Vec<usize>>();

    // Find the placement of each digit one-by-one
    for digit in 0..num_digits {
        let min_digit_index = if digit > 0 {
            max_indices[digit - 1] + 1
        } else {
            0_usize
        };
        let max_digit_index = line.len() - num_digits + digit;
        debug!(
            "digit {} min_digit_index {} max_digit_index {}",
            digit, min_digit_index, max_digit_index
        );
        for index in min_digit_index..=max_digit_index {
            if line[index] > line[max_indices[digit]] {
                #[allow(clippy::needless_range_loop)]
                for i in digit..num_digits {
                    debug!("  new max index for digit {}: {}", i, index + i - digit);
                    max_indices[i] = index + i - digit;
                }
            }
        }
        debug!(
            "digit {} max value {} at index {}",
            digit, line[max_indices[digit]], max_indices[digit]
        );
    }

    let total = (0..num_digits).fold(0, |acc, i| acc * 10 + line[max_indices[i]] as u64);
    debug!("total {}", total);
    total
}

fn parse(_input: &str) -> Vec<Vec<u8>> {
    _input
        .trim()
        .split("\n")
        .map(|line| {
            line.chars()
                .map(|c| c.to_digit(10).unwrap() as u8)
                .collect::<Vec<_>>()
        })
        .collect::<Vec<_>>()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::InputManager;

    #[test]
    fn test_part1_example() {
        let day = Day03;
        if let Some(expected) = day.part1_example_result() {
            let result = day.part1(day.part1_example()).unwrap();
            assert_eq!(result, expected);
        }
    }

    #[test]
    fn test_part2_example() {
        let day = Day03;
        if let Some(expected) = day.part2_example_result() {
            let result = day.part2(day.part2_example()).unwrap();
            assert_eq!(result, expected);
        }
    }

    #[test]
    fn test_part1_actual() {
        let day = Day03;
        if let Some(expected) = day.part1_result() {
            let input_manager = InputManager::new().unwrap();
            if let Some(input) = input_manager.get_cached_input(day.year(), day.day()) {
                let result = day.part1(&input).unwrap();
                assert_eq!(result, expected);
            }
        }
    }

    #[test]
    fn test_part2_actual() {
        let day = Day03;
        if let Some(expected) = day.part2_result() {
            let input_manager = InputManager::new().unwrap();
            if let Some(input) = input_manager.get_cached_input(day.year(), day.day()) {
                let result = day.part2(&input).unwrap();
                assert_eq!(result, expected);
            }
        }
    }
}
