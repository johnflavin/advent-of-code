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

    /// Enable debug logging
    #[arg(short, long)]
    pub debug: bool,

    /// Run only example input (do not run actual input)
    #[arg(long)]
    pub example: bool,
}
