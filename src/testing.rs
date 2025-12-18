/// Macro to generate standard test boilerplate for Solver implementations.
///
/// # Usage
///
/// ```rust,ignore
/// // For days without #[ignore] (days 1-5)
/// crate::solver_tests!(Day01);
///
/// // For days with #[ignore] (days 6+)
/// crate::solver_tests!(Day06, #[ignore]);
/// ```
///
/// # Generated Tests
///
/// - `test_part1_example`: Tests part1 with example input
/// - `test_part2_example`: Tests part2 with example input
/// - `test_part1_actual`: Tests part1 with cached actual input
/// - `test_part2_actual`: Tests part2 with cached actual input
///
/// Tests are skipped if:
/// - The expected result is `None` (puzzle not yet solved)
/// - The input file doesn't exist in the cache
#[macro_export]
macro_rules! solver_tests {
    ($day_struct:ident) => {
        $crate::solver_tests!($day_struct,);
    };
    ($day_struct:ident, $(#[$attr:meta])*) => {
        #[cfg(test)]
        mod tests {
            use super::*;
            use $crate::input::InputManager;

            #[test]
            $(#[$attr])*
            fn test_part1_example() {
                let day = $day_struct;
                if let Some(expected) = day.part1_example_result() {
                    let result = day.part1(day.part1_example()).unwrap();
                    assert_eq!(result, expected);
                }
            }

            #[test]
            $(#[$attr])*
            fn test_part2_example() {
                let day = $day_struct;
                if let Some(expected) = day.part2_example_result() {
                    let result = day.part2(day.part2_example()).unwrap();
                    assert_eq!(result, expected);
                }
            }

            #[test]
            $(#[$attr])*
            fn test_part1_actual() {
                let day = $day_struct;
                if let Some(expected) = day.part1_result() {
                    let input_manager = InputManager::new().unwrap();
                    if let Some(input) = input_manager.get_cached_input(day.year(), day.day()) {
                        let result = day.part1(&input).unwrap();
                        assert_eq!(result, expected);
                    }
                }
            }

            #[test]
            $(#[$attr])*
            fn test_part2_actual() {
                let day = $day_struct;
                if let Some(expected) = day.part2_result() {
                    let input_manager = InputManager::new().unwrap();
                    if let Some(input) = input_manager.get_cached_input(day.year(), day.day()) {
                        let result = day.part2(&input).unwrap();
                        assert_eq!(result, expected);
                    }
                }
            }
        }
    };
}
