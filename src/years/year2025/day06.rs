use crate::solver::Solver;
use anyhow::Result;
use log::debug;

pub struct Day06;

impl Solver for Day06 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        6
    }

    fn part1_example(&self) -> &str {
        "123 328  51 64
 45 64  387 23
  6 98  215 314
*   +   *   +  "
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("4277556")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("3263827")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("5595593539811")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("10153315705125")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        let lines = _input.lines().collect::<Vec<_>>();
        let (op_line, num_lines) = lines.split_last().unwrap();

        let op_strs = op_line.split_whitespace().collect::<Vec<_>>();
        let ops = op_strs
            .iter()
            .map(|op| match *op {
                "+" => std::ops::Add::add,
                "*" => std::ops::Mul::mul,
                _ => panic!("bad op: {}", op),
            })
            .collect::<Vec<_>>();
        let mut running_totals = op_strs
            .iter()
            .map(|op| match *op {
                "+" => 0,
                "*" => 1,
                _ => panic!("bad op: {}", op),
            })
            .collect::<Vec<u64>>();

        for line in num_lines {
            let nums = line
                .split_whitespace()
                .map(|s| s.parse::<u64>().unwrap())
                .collect::<Vec<_>>();

            for i in 0..nums.len() {
                running_totals[i] = ops[i](running_totals[i], nums[i]);
            }
        }

        Ok(running_totals.iter().sum::<u64>().to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        // Note: DO NOT trim input here. We rely on the whitespace for alignment.
        let lines = _input.lines().collect::<Vec<_>>();
        let (op_line, num_lines) = lines.split_last().unwrap();

        let op_strs = op_line.split_whitespace().collect::<Vec<_>>();
        let ops = op_strs
            .iter()
            .map(|op| match *op {
                "+" => std::ops::Add::add,
                "*" => std::ops::Mul::mul,
                _ => panic!("bad op: {}", op),
            })
            .collect::<Vec<_>>();
        let mut running_totals = op_strs
            .iter()
            .map(|op| match *op {
                "+" => 0,
                "*" => 1,
                _ => panic!("bad op: {}", op),
            })
            .collect::<Vec<u64>>();
        debug!("op_line: (len {}) \"{}\"", op_line.len(), op_line);

        // Build up the numbers in each column line-by-line
        let mut num_buffers = vec![String::with_capacity(num_lines.len()); op_line.len()];
        for line in num_lines {
            for (buffer, c) in num_buffers.iter_mut().zip(line.chars()) {
                buffer.push(c);
            }
        }
        debug!("num_buffers: {:?}", num_buffers);

        // Parse the numbers, apply the operators
        let mut op_idx: usize = 0;
        debug!("op: {}", op_strs[op_idx]);
        for num_buffer in num_buffers.iter().map(|nb| nb.trim()) {
            if num_buffer.trim().is_empty() {
                debug!("total: {}", running_totals[op_idx]);
                op_idx += 1;
                debug!("op: {}", op_strs[op_idx]);
                continue;
            }
            debug!("num_buffer: {}", num_buffer);
            running_totals[op_idx] =
                ops[op_idx](running_totals[op_idx], num_buffer.parse::<u64>()?);
        }

        Ok(running_totals.iter().sum::<u64>().to_string())
    }
}

crate::solver_tests!(Day06);
