use crate::solver::Solver;
use anyhow::Result;

pub struct Day09;

impl Solver for Day09 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        9
    }

    fn part1_example(&self) -> &str {
        // TODO: Add example input
        "\
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("50")
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
        Ok("0".to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        // TODO: Implement part 2 solution
        Ok("0".to_string())
    }
}

crate::solver_tests!(Day09, #[ignore]);
