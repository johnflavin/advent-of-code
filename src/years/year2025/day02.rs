use crate::solver::Solver;
use anyhow::Result;
use log::debug;

pub struct Day02;

impl Solver for Day02 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        2
    }

    fn part1_example(&self) -> &str {
        "11-22,95-115,998-1012,1188511880-1188511890,222220-222224,1698522-1698528,446443-446449,38593856-38593862,565653-565659,824824821-824824827,2121212118-2121212124"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("1227775554")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("4174379265")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("21898734247")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("28915664389")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        // Find "invalid" IDs in the ranges and add them
        // Invalid IDs are of the form XX where X is some sequence of one or more digits
        // - Corollary: Invalid IDs must be even length

        // We could just find all the numbers in the range and check them.
        // But I feel like part 2 is going to fuck us if we try that.
        // So let's think strategically.
        // If we take the first half of the numbers in the range and just copy it, then
        //   check if the number is in the range, that could be sufficient.
        // Examples:
        // 11-22 - Need to take the 1 and the 2, produce 11 and 22, they are both in range.
        // 95-115 - 99 is in range, 115 is odd so it's out
        // 998-1012 - 998 is odd so nothing, 1012->1010 which is in range.
        // I think we get the idea.

        let mut total: i64 = 0;
        for range in _input.trim().split(",") {
            debug!("{}", range);
            let (left_s, right_s) = range.split_once('-').unwrap();

            let left_even = left_s.len() % 2 == 0;
            let right_even = right_s.len() % 2 == 0;
            if !left_even && !right_even {
                debug!("Neither left {} nor right {} even", left_s, right_s);
                continue;
            }

            let range_min = left_s.parse::<i64>()?;
            let range_max = right_s.parse::<i64>()?;

            // 99 -> 9, 998 -> 9, 1698522 -> 169
            let left_first_half = if left_s.len() == 1 {
                0
            } else {
                left_s[..left_s.len() / 2].parse::<i64>()?
            };
            let right_first_half =
                right_s[..right_s.len() / 2 + (right_s.len() % 2)].parse::<i64>()?;
            // debug!("range_min: {}, range_max: {}", range_min, range_max);
            // debug!("left_first_half: {} right_first_half: {}", left_first_half, right_first_half);
            for first_half in left_first_half..=right_first_half {
                if first_half == 0 {
                    continue;
                }
                let n = first_half.ilog10() + 1;
                let duplicator = 10i64.pow(n) + 1;
                let candidate = first_half * duplicator;
                // debug!("candidate: {}", candidate);
                if range_min <= candidate && candidate <= range_max {
                    debug!(" hit: {}", candidate);
                    total += candidate;
                }
            }
        }
        Ok(total.to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        // Now we need to check any sequence of len s multiplicity m if m > 1
        // I had a whole solution written up that didn't work.
        // I'm going to do the dumbest thing imaginable:
        //  just look at every number in the range

        let mut total: u64 = 0;
        for range in _input.trim().split(",") {
            debug!("{}", range);
            let (left_s, right_s) = range.split_once('-').unwrap();
            let range_min = left_s.parse::<u64>()?;
            let range_max = right_s.parse::<u64>()?;

            for candidate in range_min..=range_max {
                let candidate_s = candidate.to_string();
                for (factor, multiplicity) in factors(candidate_s.len()) {
                    let first_n = &candidate_s[..factor];
                    if candidate == first_n.repeat(multiplicity).parse::<u64>()? {
                        debug!(" + {} ={}x{}", candidate, first_n, multiplicity);
                        total += candidate;
                        break;
                    }
                }
            }
        }
        Ok(total.to_string())
    }
}

fn factors(len: usize) -> Vec<(usize, usize)> {
    let mut factors: Vec<(usize, usize)> = vec![];
    if len == 1 {
        return factors;
    }

    factors.push((1, len));

    for factor in 2..len {
        if len.is_multiple_of(factor) {
            factors.push((factor, len / factor));
        }
    }

    factors
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_part1_example() {
        let day = Day02;
        if let Some(expected) = day.part1_example_result() {
            let result = day.part1(day.part1_example()).unwrap();
            assert_eq!(result, expected);
        }
    }

    #[test]
    fn test_part2_example() {
        let day = Day02;
        if let Some(expected) = day.part2_example_result() {
            let result = day.part2(day.part2_example()).unwrap();
            assert_eq!(result, expected);
        }
    }
}
