use clap::Parser;

#[derive(Parser)]
#[command(name = "aoc")]
#[command(about = "Run Advent of Code puzzles", long_about = None)]
pub struct Cli {
    /// Date of puzzle to run (format: YYYY-MM-DD, default: today)
    #[arg(long)]
    pub date: Option<String>,

    /// Which part to run (1 or 2, can specify multiple times)
    #[arg(short, long, value_parser = clap::value_parser!(u8).range(1..=2))]
    pub part: Vec<u8>,

    /// Run against example input only
    #[arg(long)]
    pub example: bool,

    /// Run against actual input only (explicit, also the default)
    #[arg(long)]
    pub actual: bool,

    /// Enable debug logging
    #[arg(short, long)]
    pub debug: bool,
}

impl Cli {
    /// Determine whether to run example input
    pub fn should_run_example(&self) -> bool {
        // Run example if --example flag is set
        // If neither --example nor --actual is set, don't run example (default is actual only)
        self.example
    }

    /// Determine whether to run actual input
    pub fn should_run_actual(&self) -> bool {
        // Run actual if --actual flag is set OR if neither flag is set (default behavior)
        self.actual || !self.example
    }

    /// Get list of parts to run (defaults to [1, 2])
    pub fn parts(&self) -> Vec<u8> {
        if self.part.is_empty() {
            vec![1, 2]
        } else {
            self.part.clone()
        }
    }
}
