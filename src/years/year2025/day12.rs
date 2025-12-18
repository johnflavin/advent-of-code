use crate::solver::Solver;
use anyhow::Result;

pub struct Day12;

impl Solver for Day12 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        12
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
    #[ignore]
    fn test_part1_example() {
        let day = Day12;
        if let Some(expected) = day.part1_example_result() {
            let result = day.part1(day.part1_example()).unwrap();
            assert_eq!(result, expected);
        }
    }

    #[test]
    #[ignore]
    fn test_part2_example() {
        let day = Day12;
        if let Some(expected) = day.part2_example_result() {
            let result = day.part2(day.part2_example()).unwrap();
            assert_eq!(result, expected);
        }
    }
}
