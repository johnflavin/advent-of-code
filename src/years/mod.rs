use crate::solver::Solver;

// pub mod year2024;
pub mod year2025;
/// Get a solver for a specific year and day
pub fn get_solver(year: u16, day: u8) -> Option<Box<dyn Solver>> {
    match year {
        // 2024 => year2024::get_solver(day),
        2025 => year2025::get_solver(day),
        _ => None,
    }
}
