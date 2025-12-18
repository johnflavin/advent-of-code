use crate::solver::Solver;
use anyhow::Result;

pub struct Day06;

impl Solver for Day06 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        6
    }

    fn part1_example(&self) -> &str {
        "123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +  "
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("4277556")
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

crate::solver_tests!(Day06, #[ignore]);
