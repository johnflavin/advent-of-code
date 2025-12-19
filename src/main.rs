use advent_of_code::{cli::Cli, runner::Runner, years};
use anyhow::{bail, Context, Result};
use chrono::Datelike;
use clap::Parser;
use env_logger::Env;

fn main() -> Result<()> {
    let cli = Cli::parse();

    // Configure logging
    let log_level = if cli.debug { "debug" } else { "info" };
    env_logger::Builder::from_env(Env::default().default_filter_or(log_level))
        .format_timestamp(None)
        .format_module_path(false)
        .format_target(false)
        .init();

    // Parse date (default to today)
    let date = if let Some(date_str) = &cli.date {
        chrono::NaiveDate::parse_from_str(date_str, "%Y-%m-%d")
            .context("Invalid date format. Use YYYY-MM-DD")?
    } else {
        chrono::Local::now().date_naive()
    };

    let year = date.year() as u16;
    let day = date.day() as u8;

    // Get solver
    let solver = years::get_solver(year, day)
        .ok_or_else(|| anyhow::anyhow!("No solver found for {}-12-{:02}", year, day))?;

    // Determine which parts to run
    let parts = if !cli.part.is_empty() {
        // Explicit --part flags take precedence
        cli.part.clone()
    } else if solver.part1_result().is_none() {
        // Part 1 not yet solved, only run part 1
        vec![1]
    } else {
        // Part 1 solved, run both parts
        vec![1, 2]
    };

    // Create runner
    let runner = Runner::new();

    // Run puzzle
    let success = runner.run(&*solver, &parts)?;

    if !success {
        bail!("Some tests failed");
    }

    Ok(())
}
