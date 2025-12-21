use crate::solver::{Part, Solver};
use anyhow::{Context, Result};
use arboard::Clipboard;
use log::{info, warn};

const SUCCESS_EMOJI: &str = "\u{2705}";
const FAILURE_EMOJI: &str = "\u{274C}";

#[derive(Debug, Clone)]
pub enum PartResult {
    Correct(String),
    Incorrect { actual: String, expected: String },
    Unknown(String),
}

pub struct Runner;

impl Default for Runner {
    fn default() -> Self {
        Self
    }
}

impl Runner {
    pub fn new() -> Self {
        Self
    }

    fn display_result(&self, label: &str, result: &PartResult) {
        match result {
            PartResult::Correct(value) => {
                info!("  {}: {} {}", label, value, SUCCESS_EMOJI);
            }
            PartResult::Incorrect { actual, expected } => {
                info!(
                    "  {}: actual {} ≠ expected {} {}",
                    label, actual, expected, FAILURE_EMOJI
                );
            }
            PartResult::Unknown(value) => {
                info!("  {}: {} (no expected result)", label, value);
            }
        }
    }

    fn handle_clipboard(&self, result: &PartResult) {
        if let PartResult::Unknown(value) = result {
            // No known result yet, copy to clipboard
            match Clipboard::new() {
                Ok(mut clipboard) => {
                    if let Err(e) = clipboard.set_text(value) {
                        warn!("Failed to copy to clipboard: {}", e);
                        info!("  Puzzle result: {}", value);
                    } else {
                        info!("  Puzzle result copied to clipboard: {}", value);
                    }
                }
                Err(e) => {
                    warn!("Failed to access clipboard: {}", e);
                    info!("  Puzzle result: {}", value);
                }
            }
        }
    }

    pub fn run(&self, solver: &dyn Solver, parts: &[u8], example_only: bool) -> Result<bool> {
        for &part_num in parts {
            let part = if part_num == 1 { Part::One } else { Part::Two };

            info!("Part {}", part.number());

            if example_only {
                // Only run example
                if let Some(example_result) = self.run_example(solver, part) {
                    self.display_result("Example", &example_result);
                    if matches!(example_result, PartResult::Incorrect { .. }) {
                        return Ok(false);
                    }
                } else {
                    info!("  Example failed to run for part {}", part_num);
                    return Ok(false);
                }
                continue;
            }

            // Check if this part is already solved
            let expected_result = match part {
                Part::One => solver.part1_result(),
                Part::Two => solver.part2_result(),
            };

            if expected_result.is_some() {
                // Already solved: just run actual and verify
                let actual_result = self.run_actual(solver, part)?;
                self.display_result("Actual", &actual_result);

                match actual_result {
                    PartResult::Incorrect { .. } => return Ok(false),
                    PartResult::Correct(_) => {} // Continue to next part
                    PartResult::Unknown(_) => unreachable!(), // We checked expected_result.is_some()
                }
            } else {
                // Not yet solved: run example first, then actual if example passes
                if let Some(example_result) = self.run_example(solver, part) {
                    self.display_result("Example", &example_result);

                    match example_result {
                        PartResult::Incorrect { .. } => return Ok(false),
                        PartResult::Unknown(_) => {
                            // No expected example result - stop here, don't run actual
                            info!("  No expected example result set. Set part{}_example_result() to proceed.", part_num);
                            return Ok(true);
                        }
                        PartResult::Correct(_) => {} // Continue to actual
                    }
                }

                // Example passed, run actual
                let actual_result = self.run_actual(solver, part)?;
                self.display_result("Actual", &actual_result);
                self.handle_clipboard(&actual_result);

                // Stop after running unsolved part (result copied to clipboard)
                return Ok(true);
            }
        }

        Ok(true)
    }

    fn run_example(&self, solver: &dyn Solver, part: Part) -> Option<PartResult> {
        let example_input = match part {
            Part::One => solver.part1_example(),
            Part::Two => solver.part2_example(),
        };

        // Always run the example
        let actual_result = match part {
            Part::One => solver.part1(example_input),
            Part::Two => solver.part2(example_input),
        };

        let expected_result = match part {
            Part::One => solver.part1_example_result(),
            Part::Two => solver.part2_example_result(),
        };

        match actual_result {
            Ok(actual) => match expected_result {
                Some(expected) => {
                    if actual == expected {
                        Some(PartResult::Correct(actual))
                    } else {
                        Some(PartResult::Incorrect {
                            actual,
                            expected: expected.to_owned(),
                        })
                    }
                }
                None => Some(PartResult::Unknown(actual)),
            },
            Err(_) => None,
        }
    }

    fn run_actual(&self, solver: &dyn Solver, part: Part) -> Result<PartResult> {
        let input = solver
            .get_actual_input()
            .context("Failed to get actual input")?;

        let actual = match part {
            Part::One => solver.part1(&input),
            Part::Two => solver.part2(&input),
        }
        .context("Failed to solve actual input")?;

        let expected = match part {
            Part::One => solver.part1_result(),
            Part::Two => solver.part2_result(),
        };

        match expected {
            Some(expected) => {
                let result = if actual == expected {
                    PartResult::Correct(actual)
                } else {
                    PartResult::Incorrect {
                        actual,
                        expected: expected.to_owned(),
                    }
                };
                Ok(result)
            }
            None => Ok(PartResult::Unknown(actual)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Mock solver for testing runner behavior
    struct MockSolver {
        part1_example_result: Option<&'static str>,
        part2_example_result: Option<&'static str>,
        part1_result: Option<&'static str>,
        part2_result: Option<&'static str>,
        /// Track which methods were called
        calls: std::cell::RefCell<Vec<String>>,
    }

    impl MockSolver {
        fn new() -> Self {
            Self {
                part1_example_result: None,
                part2_example_result: None,
                part1_result: None,
                part2_result: None,
                calls: std::cell::RefCell::new(Vec::new()),
            }
        }

        fn with_part1_example_result(mut self, result: &'static str) -> Self {
            self.part1_example_result = Some(result);
            self
        }

        fn with_part2_example_result(mut self, result: &'static str) -> Self {
            self.part2_example_result = Some(result);
            self
        }

        fn with_part1_result(mut self, result: &'static str) -> Self {
            self.part1_result = Some(result);
            self
        }

        fn with_part2_result(mut self, result: &'static str) -> Self {
            self.part2_result = Some(result);
            self
        }

        fn get_calls(&self) -> Vec<String> {
            self.calls.borrow().clone()
        }
    }

    impl Solver for MockSolver {
        fn year(&self) -> u16 {
            2024
        }
        fn day(&self) -> u8 {
            1
        }

        fn part1_example(&self) -> &str {
            "example1"
        }
        fn part2_example(&self) -> &str {
            "example2"
        }

        fn part1_example_result(&self) -> Option<&str> {
            self.part1_example_result
        }
        fn part2_example_result(&self) -> Option<&str> {
            self.part2_example_result
        }

        fn part1_result(&self) -> Option<&str> {
            self.part1_result
        }
        fn part2_result(&self) -> Option<&str> {
            self.part2_result
        }

        fn part1(&self, input: &str) -> Result<String> {
            self.calls.borrow_mut().push(format!("part1({})", input));
            // Return "42" for both example and actual
            Ok("42".to_string())
        }

        fn part2(&self, input: &str) -> Result<String> {
            self.calls.borrow_mut().push(format!("part2({})", input));
            // Return "100" for both example and actual
            Ok("100".to_string())
        }

        fn get_actual_input(&self) -> Result<String> {
            self.calls.borrow_mut().push("get_actual_input".to_string());
            Ok("actual_input".to_string())
        }
    }

    #[test]
    fn test_example_only_with_expected_result_correct() {
        let solver = MockSolver::new().with_part1_example_result("42");
        let runner = Runner::new();

        let result = runner.run(&solver, &[1], true);
        assert!(result.is_ok());
        assert!(result.unwrap()); // Should succeed

        let calls = solver.get_calls();
        assert_eq!(calls, vec!["part1(example1)"]);
        // Should NOT call get_actual_input
        assert!(!calls.contains(&"get_actual_input".to_string()));
    }

    #[test]
    fn test_example_only_with_expected_result_incorrect() {
        let solver = MockSolver::new().with_part1_example_result("wrong");
        let runner = Runner::new();

        let result = runner.run(&solver, &[1], true);
        assert!(result.is_ok());
        assert!(!result.unwrap()); // Should fail (incorrect)

        let calls = solver.get_calls();
        assert_eq!(calls, vec!["part1(example1)"]);
    }

    #[test]
    fn test_example_only_without_expected_result() {
        let solver = MockSolver::new(); // No example result set
        let runner = Runner::new();

        let result = runner.run(&solver, &[1], true);
        assert!(result.is_ok());
        assert!(result.unwrap()); // Should succeed (Unknown is not failure)

        let calls = solver.get_calls();
        assert_eq!(calls, vec!["part1(example1)"]);
        // Should NOT call get_actual_input
        assert!(!calls.contains(&"get_actual_input".to_string()));
    }

    #[test]
    fn test_unsolved_with_example_result_runs_actual() {
        // Unsolved (no part1_result) but has example_result
        let solver = MockSolver::new().with_part1_example_result("42");
        let runner = Runner::new();

        let result = runner.run(&solver, &[1], false);
        assert!(result.is_ok());

        let calls = solver.get_calls();
        // Should run example first, then actual
        assert_eq!(
            calls,
            vec!["part1(example1)", "get_actual_input", "part1(actual_input)"]
        );
    }

    #[test]
    fn test_unsolved_without_example_result_stops() {
        // Unsolved and no example_result - should run example, show Unknown, stop
        let solver = MockSolver::new();
        let runner = Runner::new();

        let result = runner.run(&solver, &[1], false);
        assert!(result.is_ok());
        assert!(result.unwrap()); // Should succeed (stopped gracefully)

        let calls = solver.get_calls();
        // Should only run example, NOT actual
        assert_eq!(calls, vec!["part1(example1)"]);
        assert!(!calls.contains(&"get_actual_input".to_string()));
    }

    #[test]
    fn test_solved_skips_example() {
        // Already solved - should skip example, just verify actual
        let solver = MockSolver::new()
            .with_part1_result("42")
            .with_part1_example_result("42");
        let runner = Runner::new();

        let result = runner.run(&solver, &[1], false);
        assert!(result.is_ok());

        let calls = solver.get_calls();
        // Should NOT run example, just actual
        assert_eq!(calls, vec!["get_actual_input", "part1(actual_input)"]);
    }

    #[test]
    fn test_part2_unsolved_without_example_result_stops() {
        // Part 2 unsolved with no example result
        let solver = MockSolver::new()
            .with_part1_result("42")
            .with_part1_example_result("42");
        // part2_example_result is None
        let runner = Runner::new();

        let result = runner.run(&solver, &[2], false);
        assert!(result.is_ok());

        let calls = solver.get_calls();
        // Should run part2 example, then stop (not run actual)
        assert_eq!(calls, vec!["part2(example2)"]);
        assert!(!calls.contains(&"get_actual_input".to_string()));
    }

    #[test]
    fn test_example_only_runs_multiple_parts() {
        let solver = MockSolver::new()
            .with_part1_example_result("42")
            .with_part2_example_result("100");
        let runner = Runner::new();

        let result = runner.run(&solver, &[1, 2], true);
        assert!(result.is_ok());
        assert!(result.unwrap());

        let calls = solver.get_calls();
        // Should run both examples
        assert_eq!(calls, vec!["part1(example1)", "part2(example2)"]);
    }
}
