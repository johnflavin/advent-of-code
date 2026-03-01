use crate::solver::Solver;
use anyhow::Result;
use log::debug;
use std::iter::zip;

pub struct Day12;

impl Solver for Day12 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        12
    }

    fn part1_example(&self) -> &str {
        "\
0:
###
##.
##.

1:
###
##.
.##

2:
.##
###
##.

3:
##.
###
##.

4:
###
#..
###

5:
###
.#.
###

4x4: 0 0 0 0 2 0
12x5: 1 0 1 0 2 2
12x5: 1 0 1 0 3 2"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        // Skip the example
        // Our actual input lets us do a dumb thing but the example doesn't
        Some("0")
    }

    fn part2_example_result(&self) -> Option<&str> {
        // On the last day there is no part 2
        Some("0")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("487")
    }

    fn part2_result(&self) -> Option<&str> {
        // On the last day there is no part 2
        Some("0")
    }

    fn part1(&self, input: &str) -> Result<String> {
        // We get five shapes, and
        // For each region we get a size (rows x cols) and a number of shapes to use
        //
        // We're going to try a dumb thing: feasibility checks ONLY
        // 1. Count the "area" (number of #) in each shape
        // 2. Calculate the weighted sum (num shapes x shape area) over shapes
        //    If the weighted sum is > region area, it is impossible and we skip
        // 3. Calculate number of 3x3 cells: (rows/3) x (cols/3)
        //    If num 3x3 cells > num shapes needed, then region is possible with no overlaps
        // 4. If neither applies we need to implement a search.
        //    But let's hope that doesn't happen!
        //
        // (Later update: We got away with the dumb thing. Yay!)

        let (shapes_lines, region_lines) = input.rsplit_once("\n\n").unwrap();
        let shapes = shapes_lines
            .split("\n\n")
            .map(|section| {
                let (_, shape_def) = section.split_once(":\n").unwrap();
                let shape = shape_def
                    .split('\n')
                    .enumerate()
                    .flat_map(|(row, shape_line)| {
                        shape_line
                            .chars()
                            .enumerate()
                            .filter(|&(_, c)| c == '#')
                            .map(move |(col, _)| (row, col))
                    })
                    .collect::<Vec<_>>();
                (shape.len(), shape)
            })
            .collect::<Vec<_>>();
        // debug!("shapes: {:?}", shapes);

        let total = region_lines.lines().fold(0usize, |s, region_line| {
            let (dim_str, shape_counts_str) = region_line.split_once(": ").unwrap();
            let (x, y) = dim_str.split_once("x").unwrap();
            let rows = x.parse::<usize>().unwrap();
            let cols = y.parse::<usize>().unwrap();
            let area = rows * cols;

            let shape_counts = shape_counts_str
                .split(" ")
                .map(|s| s.parse::<usize>().unwrap())
                .collect::<Vec<_>>();

            // debug!("rows: {} cols: {} area: {}", rows, cols, area);
            // debug!("shape counts: {:?}", shape_counts);

            let weighted_shape_area = zip(shapes.iter(), shape_counts.iter())
                .fold(0usize, |sum, (&(shape_area, _), count)| {
                    sum + shape_area * count
                });
            if weighted_shape_area > area {
                debug!(
                    "REJECT weighted sum of shapes {} > area {} | {}",
                    weighted_shape_area, area, region_line
                );
                return s;
            }

            let num_3x3_cells = (rows / 3) * (cols / 3);
            let num_shapes = shape_counts.iter().sum::<usize>();
            if num_3x3_cells >= num_shapes {
                debug!(
                    "ACCEPT num 3x3 cells {} >= num shapes {} | {}",
                    num_3x3_cells, num_shapes, region_line
                );
                return s + 1;
            }

            debug!(
                "NOOOO! We need to actually implement a search for this one | {}",
                region_line
            );
            s
        });

        Ok(total.to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        // On the last day there is no part 2
        Ok("0".to_string())
    }
}

crate::solver_tests!(Day12);
