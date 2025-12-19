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

    pub fn run(&self, solver: &dyn Solver, parts: &[u8]) -> Result<bool> {
        for &part_num in parts {
            let part = if part_num == 1 { Part::One } else { Part::Two };

            info!("Part {}", part.number());

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

                    if matches!(example_result, PartResult::Incorrect { .. }) {
                        return Ok(false);
                    }
                }

                // Example passed (or no example), run actual
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

        let expected_result = match part {
            Part::One => solver.part1_example_result(),
            Part::Two => solver.part2_example_result(),
        };

        if let Some(expected) = expected_result {
            let actual_result = match part {
                Part::One => solver.part1(example_input),
                Part::Two => solver.part2(example_input),
            };

            if let Ok(actual) = actual_result {
                let result = if actual == expected {
                    PartResult::Correct(actual)
                } else {
                    PartResult::Incorrect {
                        actual,
                        expected: expected.to_owned(),
                    }
                };
                return Some(result);
            }
        }
        None
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
