use crate::solver::{Part, Solver};
use anyhow::{Context, Result};
use arboard::Clipboard;
use log::{info, warn};

const SUCCESS_EMOJI: &str = "\u{2705}";
const FAILURE_EMOJI: &str = "\u{274C}";

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

    pub fn run(&self, solver: &dyn Solver, parts: &[u8]) -> Result<bool> {
        let mut all_success = true;

        for &part_num in parts {
            let part = if part_num == 1 { Part::One } else { Part::Two };

            info!("Part {}", part.number());

            let part_success = self.run_part(solver, part)?;
            all_success = all_success && part_success;

            // If part 1 fails and we're running both parts, stop
            if !part_success && parts.len() > 1 && part == Part::One {
                warn!("Part 1 failed, skipping part 2");
                return Ok(false);
            }
        }

        Ok(all_success)
    }

    fn run_part(&self, solver: &dyn Solver, part: Part) -> Result<bool> {
        let mut success = true;

        // Run example if requested
        if self.run_example {
            let example_success = self.run_example(solver, part)?;
            success = success && example_success;

            // If example fails, don't run actual
            if !example_success {
                return Ok(false);
            }
        }

        // Run actual if requested
        if self.run_actual {
            let actual_success = self.run_actual(solver, part)?;
            success = success && actual_success;
        }

        Ok(success)
    }

    fn run_example(&self, solver: &dyn Solver, part: Part) -> Result<bool> {
        let example_input = match part {
            Part::One => solver.part1_example(),
            Part::Two => solver.part2_example(),
        };

        let expected = match part {
            Part::One => solver.part1_example_result(),
            Part::Two => solver.part2_example_result(),
        };

        if example_input.is_empty() {
            info!("  Example: None provided");
            return Ok(true);
        }

        let actual = match part {
            Part::One => solver.part1(example_input),
            Part::Two => solver.part2(example_input),
        }
        .context("Failed to solve example")?;

        match expected {
            Some(expected) => {
                let success = actual == expected;
                let emoji = if success {
                    SUCCESS_EMOJI
                } else {
                    FAILURE_EMOJI
                };
                let eq = if success { "=" } else { "≠" };

                info!(
                    "  Example: actual {} {} expected {} {}",
                    actual, eq, expected, emoji
                );

                Ok(success)
            }
            None => {
                info!("  Example: {} (no expected result to compare)", actual);
                Ok(true)
            }
        }
    }

    fn run_actual(&self, solver: &dyn Solver, part: Part) -> Result<bool> {
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
                let success = actual == expected;
                let emoji = if success {
                    SUCCESS_EMOJI
                } else {
                    FAILURE_EMOJI
                };
                let eq = if success { "=" } else { "≠" };

                info!(
                    "  Puzzle: actual {} {} expected {} {}",
                    actual, eq, expected, emoji
                );

                Ok(success)
            }
            None => {
                // No known result yet, copy to clipboard
                match Clipboard::new() {
                    Ok(mut clipboard) => {
                        if let Err(e) = clipboard.set_text(&actual) {
                            warn!("Failed to copy to clipboard: {}", e);
                            info!("  Puzzle result: {}", actual);
                        } else {
                            info!("  Puzzle result copied to clipboard: {}", actual);
                        }
                    }
                    Err(e) => {
                        warn!("Failed to access clipboard: {}", e);
                        info!("  Puzzle result: {}", actual);
                    }
                }

                Ok(true)
            }
        }
    }
}
