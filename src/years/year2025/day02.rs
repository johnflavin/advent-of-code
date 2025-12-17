use crate::solver::Solver;
use anyhow::Result;
use log::debug;
use std::collections::HashSet;

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
        // Note: This did get me the answer.
        //
        // No, this sucks. It is so slow.
        // Not only am I generating numbers I know I don't need, I'm
        //   converting them to strings and back.
        // I could skip the string part by checking if the numbers are multiples of
        // things like 111, 101, 1001001, etc. depending on the length.
        // But I would still be generating a lot of numbers that don't match.
        // Better to use those multiples of 1s and 0s above to generate the numbers.
        // Then I don't need to check anything, except maybe one or two on the ends.
        // Two problems:
        // 1. How do I programmatically generate those multiples given a range?
        // 2. How do I know what to multiply them by? For instance, it's all good to know
        //   two-digit ranges need 11, but how do I go from there to 11, 22, 33 etc. without
        //   just generating them all?
        // Examples
        // 5210718-5346163
        // Length left 7 right 7
        // Factors (1,7) (prime; this reasoning goes for any prime)
        // 1111111 = sum_0^{7-1} 10^{1*i}
        // Span-1 left 5 right 5
        // Candidate 5555555
        //
        // 648632326-648673051
        // Length left 9 right 9
        // Factors (1,9) (3,3)
        // 111111111 = sum_0^{9-1} 10^{1*i}
        // Span-1 left 6 right 6
        // Candidate 666666666
        // 001001001 = sum_0^{3-1} 10^{3*i}
        // Span-3 left 648 right 648
        // Candidate 648648648
        //
        // 1255-1813
        // Length left 4 right 4
        // Factors (1,4) (2,2)
        // 1111 = sum_0^{4-1} 10^{1*i}
        // Span-1 left 1 right 1
        // Candidate 1111
        // 0101 = sum_0^{2-1} 10^{2*i}
        // Span-2 left 12 right 18
        // Candidates 1212 1313 1414 1515 1616 1717 1818
        //
        // For mixed-length ranges maybe I split them into two ranges of consistent length

        let mut total: u64 = 0;
        for range in _input.trim().split(",") {
            debug!("{}", range);
            let (left_s, right_s) = range.split_once('-').unwrap();

            let range_min = left_s.parse::<u64>()?;
            let range_max = right_s.parse::<u64>()?;

            let mut candidates = HashSet::new();
            if left_s.len() == right_s.len() {
                candidates.extend(generate_candidates(left_s, right_s));
            } else {
                let first_subrange_right = (10_u64.pow(left_s.len() as u32) - 1).to_string();
                let second_subrange_left = 10_u64.pow(right_s.len() as u32 - 1).to_string();
                candidates.extend(generate_candidates(left_s, &first_subrange_right));
                candidates.extend(generate_candidates(&second_subrange_left, right_s));
            }

            for candidate in candidates {
                if range_min <= candidate && candidate <= range_max {
                    debug!(" + {}", candidate);
                    total += candidate;
                } else {
                    debug!("   {}", candidate);
                }
            }
        }
        Ok(total.to_string())
    }
}

fn generate_candidates(left_s: &str, right_s: &str) -> HashSet<u64> {
    let len = left_s.len();
    if len != right_s.len() {
        panic!(
            "This function only accepts homogeneous length range strings. Input: {} {}",
            left_s, right_s
        );
    }
    let mut candidates = HashSet::new();
    if len == 1 {
        return candidates;
    }
    for (factor1, factor2) in factors(left_s.len()) {
        let multiple = (0..factor2)
            .map(|i| 10_u64.pow((factor1 * i) as u32))
            .sum::<u64>();

        // Take the first factor1 digits from left and right
        let left_n = first_n(left_s, factor1);
        let right_n = first_n(right_s, factor1);
        debug!(
            "factor ({}, {}) multiple {} left-{} {} right-{} {}",
            factor1, factor2, multiple, factor1, left_n, factor1, right_n
        );
        candidates.extend((left_n..=right_n).map(|i| i * multiple));
    }

    candidates
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

fn first_n(digits: &str, n: usize) -> u64 {
    digits[..n].parse::<u64>().unwrap()
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
