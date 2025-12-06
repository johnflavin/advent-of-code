use anyhow::Result;

/// Which part of the puzzle to solve
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Part {
    One,
    Two,
}

impl Part {
    pub fn number(&self) -> u8 {
        match self {
            Part::One => 1,
            Part::Two => 2,
        }
    }
}

/// Trait that all daily puzzle solutions must implement
pub trait Solver {
    /// The year of this puzzle (e.g., 2024)
    fn year(&self) -> u16;

    /// The day of this puzzle (1-25)
    fn day(&self) -> u8;

    /// Example input for part 1
    fn part1_example(&self) -> &str;

    /// Example input for part 2 (often same as part1_example)
    fn part2_example(&self) -> &str;

    /// Expected result for part 1 example
    fn part1_example_result(&self) -> Option<&str>;

    /// Expected result for part 2 example
    fn part2_example_result(&self) -> Option<&str>;

    /// Known result for part 1 actual input (None if not yet solved)
    fn part1_result(&self) -> Option<&str>;

    /// Known result for part 2 actual input (None if not yet solved)
    fn part2_result(&self) -> Option<&str>;

    /// Solve part 1 with the given input
    fn part1(&self, input: &str) -> Result<String>;

    /// Solve part 2 with the given input
    fn part2(&self, input: &str) -> Result<String>;

    /// Get the actual puzzle input from cache or download it
    fn get_actual_input(&self) -> Result<String> {
        crate::input::InputManager::new()?.get_input(self.year(), self.day())
    }
}
