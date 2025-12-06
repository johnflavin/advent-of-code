// Utility module for common Advent of Code helpers
// Add grid utilities, range operations, parsing helpers, etc. as needed

/// Split input into lines, trimming trailing newline
///
/// This mimics the Python implementation which does `input.rstrip("\n").split("\n")`
pub fn lines(input: &str) -> impl Iterator<Item = &str> {
    input.trim_end_matches('\n').split('\n')
}

/// Split input into lines and collect to Vec
pub fn lines_vec(input: &str) -> Vec<&str> {
    lines(input).collect()
}

/// Split input into non-empty lines
pub fn nonempty_lines(input: &str) -> impl Iterator<Item = &str> {
    lines(input).filter(|line| !line.is_empty())
}
