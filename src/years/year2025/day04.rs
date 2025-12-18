use crate::solver::Solver;
use anyhow::Result;
use std::collections::HashSet;

pub struct Day04;

const NEIGHBOR_COORDS: [(i8, i8); 8] = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
];

impl Solver for Day04 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        4
    }

    fn part1_example(&self) -> &str {
        "..@@.@@@@.
@@@.@.@.@@
@@@@@.@.@@
@.@@@@..@.
@@.@@@@.@@
.@@@@@@@.@
.@.@.@.@@@
@.@@@.@@@@
.@@@@@@@@.
@.@.@@@.@."
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("13")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("43")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("1424")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("8727")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        let (paper_locations, num_cols, num_rows) = parse(_input);
        let mut total = 0;
        for location in &paper_locations {
            if find_num_occupied_neighbors(&paper_locations, num_cols, num_rows, location) < 4 {
                total += 1;
            }
        }
        Ok(total.to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        let (mut paper_locations, num_cols, num_rows) = parse(_input);

        let mut did_remove_some_this_round = true;
        let mut removed = 0;
        while did_remove_some_this_round {
            did_remove_some_this_round = false;
            let mut next_paper_locations = paper_locations.clone();

            for location in &paper_locations {
                if find_num_occupied_neighbors(&paper_locations, num_cols, num_rows, location) < 4 {
                    removed += 1;
                    next_paper_locations.remove(location);
                    did_remove_some_this_round = true;
                }
            }
            paper_locations = next_paper_locations;
        }
        Ok(removed.to_string())
    }
}

fn find_num_occupied_neighbors(
    paper_locations: &HashSet<(i32, i32)>,
    num_cols: u16,
    num_rows: u16,
    location: &(i32, i32),
) -> i32 {
    let mut num_occupied_neighbors = 0;
    for (dx, dy) in NEIGHBOR_COORDS.iter() {
        let neighbor_x = location.0 + *dx as i32;
        let neighbor_y = location.1 + *dy as i32;
        if neighbor_x >= 0
            && neighbor_y >= 0
            && neighbor_x < num_rows as i32
            && neighbor_y < num_cols as i32
        {
            num_occupied_neighbors += if paper_locations.contains(&(neighbor_x, neighbor_y)) {
                1
            } else {
                0
            };
        }
    }
    num_occupied_neighbors
}

fn parse(_input: &str) -> (HashSet<(i32, i32)>, u16, u16) {
    let mut locations = HashSet::new();
    let (mut max_x, mut max_y) = (0, 0);
    for (y, line) in _input.trim().split("\n").enumerate() {
        for (x, ch) in line.trim().chars().enumerate() {
            if ch == '@' {
                locations.insert((x as i32, y as i32));
            }
            if x > max_x {
                max_x = x;
            }
        }
        if y > max_y {
            max_y = y;
        }
    }
    (locations, (max_y + 1) as u16, (max_x + 1) as u16)
}

crate::solver_tests!(Day04);
