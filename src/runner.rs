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

pub struct RunResult {
    pub example: Option<PartResult>,
    pub actual: Option<PartResult>,
}

pub struct Runner {
    run_example: bool,
    run_actual: bool,
}

impl Runner {
    pub fn new(run_example: bool, run_actual: bool) -> Self {
        Self {
            run_example,
            run_actual,
        }
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

            let part_result = self.run_part(solver, part)?;

            if let Some(example_result) = part_result.example {
                self.display_result("Example", &example_result);

                if matches!(example_result, PartResult::Incorrect { .. }) {
                    return Ok(false);
                }
            }

            if let Some(actual_result) = part_result.actual {
                self.display_result("Actual", &actual_result);
                self.handle_clipboard(&actual_result);

                match actual_result {
                    PartResult::Incorrect { .. } => return Ok(false),
                    PartResult::Unknown(_) => return Ok(true),
                    PartResult::Correct(_) => {}
                }
            }
        }

        Ok(true)
    }

    fn run_part(&self, solver: &dyn Solver, part: Part) -> Result<RunResult> {
        let mut example_result = None;

        // Run example if requested
        if self.run_example {
            example_result = self.run_example(solver, part);

            if let Some(PartResult::Incorrect { .. }) = example_result {
                // If example fails return early, don't run actual
                return Ok(RunResult {
                    example: example_result,
                    actual: None,
                });
            }
        }

        // Run actual if requested
        let actual_result = if self.run_actual {
            Some(self.run_actual(solver, part)?)
        } else {
            None
        };

        Ok(RunResult {
            example: example_result,
            actual: actual_result,
        })
    }

    fn run_example(&self, solver: &dyn Solver, part: Part) -> Option<PartResult> {
        let example_input = match part {
            Part::One => solver.part1_example(),
            Part::Two => solver.part2_example(),
        };

        let expected = match part {
            Part::One => solver.part1_example_result(),
            Part::Two => solver.part2_example_result(),
        };

        if example_input.is_empty() {
            return None;
        }

        let actual_result = match part {
            Part::One => solver.part1(example_input),
            Part::Two => solver.part2(example_input),
        };

        if let Ok(actual) = actual_result {
            let result = if actual == expected? {
                PartResult::Correct(actual)
            } else {
                PartResult::Incorrect {
                    actual,
                    expected: expected?.to_owned(),
                }
            };
            return Some(result);
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
