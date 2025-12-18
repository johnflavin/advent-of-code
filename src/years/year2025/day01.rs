use crate::solver::Solver;
use crate::util::lines;
use anyhow::Result;
use log::debug;
use num_integer::div_rem;

pub struct Day01;

impl Solver for Day01 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        1
    }

    fn part1_example(&self) -> &str {
        "L68
L30
R48
L5
R60
L55
L1
L99
R14
L82"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("3")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("6")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("1036")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("6228")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        let mut zero_count = 0;
        let mut pointer = 50;
        for line in lines(_input) {
            debug!("{}", line);
            let turn: i32 = match &line[..1] {
                "L" => -line[1..].parse()?,
                "R" => line[1..].parse()?,
                _ => panic!("Cannot parse line {}", line),
            };
            pointer += turn;
            pointer %= 100;
            debug!("pointer: {}", pointer);
            if pointer == 100 || pointer == 0 {
                zero_count += 1;
                debug!("Count: {}", zero_count);
            }
        }
        Ok(zero_count.to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        let mut zero_count = 0;
        let mut pointer = 50;

        for line in lines(_input) {
            let turn: i16 = match &line[..1] {
                "L" => -line[1..].parse()?,
                "R" => line[1..].parse()?,
                _ => panic!("Cannot parse line {}", line),
            };
            let new_pointer = pointer + turn;

            debug!("{} {} = {}", pointer, line, new_pointer);

            let (division, remainder) = div_rem(new_pointer, 100);

            if division > 0 {
                // We are at or above 100
                // We don't care about remainder because even if we're at 100 exactly this is correct
                zero_count += division;
                debug!("  +{} = {}", division, zero_count);
            } else if division <= 0 {
                // We could be negative, or we could be in [0, 99)
                zero_count -= division;
                if division < 0 {
                    debug!("  +{} = {}", division.abs(), zero_count);
                }

                // Check for a zero crossing
                if pointer != 0 && remainder <= 0 {
                    zero_count += 1;
                    debug!("  +1 = {} | zero crossing", zero_count);
                }
            }

            if remainder < 0 {
                pointer = remainder + 100;
            } else {
                pointer = remainder;
            }
        }
        Ok(zero_count.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::InputManager;

    #[test]
    fn test_part1_example() {
        let day = Day01;
        if let Some(expected) = day.part1_example_result() {
            let result = day.part1(day.part1_example()).unwrap();
            assert_eq!(result, expected);
        }
    }

    #[test]
    fn test_part2_example() {
        let day = Day01;
        if let Some(expected) = day.part2_example_result() {
            let result = day.part2(day.part2_example()).unwrap();
            assert_eq!(result, expected);
        }
    }

    #[test]
    fn test_part1_actual() {
        let day = Day01;
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
        let day = Day01;
        if let Some(expected) = day.part2_result() {
            let input_manager = InputManager::new().unwrap();
            if let Some(input) = input_manager.get_cached_input(day.year(), day.day()) {
                let result = day.part2(&input).unwrap();
                assert_eq!(result, expected);
            }
        }
    }
}
