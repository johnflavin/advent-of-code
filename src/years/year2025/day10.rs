use crate::solver::{Part, Solver};
use anyhow::Result;
use log::debug;
use std::collections::{HashSet, VecDeque};

pub struct Day10;

const EPSILON: f64 = 1e-10;

impl Solver for Day10 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        10
    }

    fn part1_example(&self) -> &str {
        // TODO: Add example input
        "\
[.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
[...#.] (0,2,3,4) (2,3) (0,4) (0,1,2) (1,2,3,4) {7,5,12,7,2}
[.###.#] (0,1,2,3,4) (0,3,4) (0,1,2,4,5) (1,2) {10,11,11,5,10,5}"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("7")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("33")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("475")
    }

    fn part2_result(&self) -> Option<&str> {
        // TODO: Add known result for part 2
        None
    }

    /**
    Pathfinding!
    We have a starting node and an ending node, and movements between nodes.
    Find the shortest path.

    Question is how to represent the node.
    A Vec<bool>? That could work.

    Shower thought: encode as a binary number. Transitions are XORs.
    */
    fn part1(&self, input: &str) -> Result<String> {
        let total = input.trim().lines().fold(0usize, |total, line| {
            let (target_vec, transition_idx_vec) = Self::parse(line, Part::One);
            let target = target_vec
                .iter()
                .fold(0usize, |s, idx| s + (1 << idx) as usize);
            let transitions = transition_idx_vec
                .iter()
                .map(|transition_idx_vec| {
                    transition_idx_vec
                        .iter()
                        .fold(0usize, |s, idx| s + (1 << idx) as usize)
                })
                .collect::<Vec<_>>();
            total + Self::solve_part1(target, &transitions)
        });
        Ok(total.to_string())
    }
    /**
    I started trying to solve this the same way as part 1 and... no.
    What I tried there is instead of treating the basis numbers as encoding binary digits,
    I made them base b digits instead, where b was 1 + the biggest number in the target set.
    That was a mistake.

    This really seems more like a linear programming problem.
    But I don't know what that means exactly or how to solve it!
    */
    fn part2(&self, input: &str) -> Result<String> {
        let total = input.trim().lines().fold(0usize, |total, line| {
            let (target, transition_idx_vec) = Self::parse(line, Part::Two);
            let basis = transition_idx_vec
                .iter()
                .map(|transition_idx_vec| {
                    let mut transition = vec![0; target.len()];
                    transition_idx_vec
                        .iter()
                        .for_each(|idx| transition[*idx] = 1);
                    transition
                })
                .collect::<Vec<_>>();
            total + Self::solve_part2(&target, &basis)
        });

        Ok(total.to_string())
    }
}

impl Day10 {
    fn solve_part1(target: usize, transitions: &[usize]) -> usize {
        let mut stack = VecDeque::new();
        // Stack: (current value, number of steps)
        stack.push_front((0usize, 0usize));

        let mut seen = HashSet::new();

        while let Some((current_value, num_steps)) = stack.pop_back() {
            if seen.contains(&current_value) {
                continue;
            }
            seen.insert(current_value);
            if current_value == target {
                return num_steps;
            }

            transitions.iter().for_each(|&transition| {
                stack.push_front((current_value ^ transition, num_steps + 1))
            })
        }

        0
    }

    fn solve_part2(target: &[usize], vectors: &[Vec<usize>]) -> usize {
        debug!("target {:?} vectors {:?}", target, vectors);
        let n = vectors.len();
        let d = target.len();

        // Arrange vectors into columns of matrix A
        let mut a = (0..vectors[0].len()).map(|_| vec![]).collect::<Vec<_>>();
        for v in vectors {
            for (item, a_row) in v.iter().zip(&mut a) {
                a_row.push(item);
            }
        }

        // Find initial feasible solution
        let mut basis = (0..d).map(|i| n + i).collect::<Vec<_>>();

        // Create extended tableau with artificial variables
        // [A | I | b] where I is d×d identity for artificial vars
        let mut tableau: Vec<Vec<isize>> = Vec::with_capacity(d);
        debug!("initial tableau:");
        for (i, t) in target.iter().enumerate() {
            let mut tableau_row = vec![0; n + d + 1];
            // A
            (0..n).for_each(|j| tableau_row[j] = vectors[j][i] as isize);
            // Identity matrix representing artifical variables
            tableau_row[n + i] = 1;
            // b
            tableau_row[n + d] = *t as isize;

            debug!(" {:?}", tableau_row);
            tableau.push(tableau_row);
        }

        let mut phase1_cost = Vec::with_capacity(d + n);
        (0..(d + n)).for_each(|i| phase1_cost.push(if i < n { 0 } else { 1 }));

        // Find entering variable (most negative reduced cost)
        while let Some(entering) = Self::find_entering(&tableau, &phase1_cost, &basis) {
            // Find leaving variable (minimum ratio test)
            let leaving_opt = Self::find_leaving(&tableau, &entering);
            if Option::is_none(&leaving_opt) {
                panic!("unbounded");
            }
            let leaving = leaving_opt.unwrap();

            Self::pivot(&mut tableau, &entering, &leaving);

            basis[leaving] = entering;

            debug!(" {:?}", tableau);
        }

        // Optimize actual objective (sum of coefficients)
        0
    }

    fn find_entering(tableau: &[Vec<isize>], cost: &[usize], basis: &[usize]) -> Option<usize> {
        // Compute reduced costs for non-basic variables
        // reduced_cost[j] = c[j] - basis_cost^T * A[j]

        let mut min_reduced_cost = 0;
        let mut entering = None;

        for j in 0..tableau.len() - 1 {
            if basis.contains(&j) {
                continue;
            }

            // Compute reduced cost
            let mut reduced_cost = cost[j] as isize;
            for (i, basis_var) in basis.iter().enumerate() {
                reduced_cost -= (cost[*basis_var] as isize) * tableau[i][j];
            }

            if reduced_cost < min_reduced_cost {
                min_reduced_cost = reduced_cost;
                entering = Some(j);
            }
        }

        entering
    }

    fn find_leaving(tableau: &[Vec<isize>], entering_col: &usize) -> Option<usize> {
        // Minimum ratio test: min(b[i] / A[i][entering]) for A[i][entering] > 0

        let mut min_ratio = f64::INFINITY;
        let mut leaving = None;

        for (i, tableau_row) in tableau.iter().enumerate() {
            if tableau_row[*entering_col] as f64 > EPSILON {
                let ratio =
                    tableau_row[tableau_row.len() - 1] as f64 / tableau_row[*entering_col] as f64;
                if ratio < min_ratio {
                    min_ratio = ratio;
                    leaving = Some(i);
                }
            }
        }

        leaving
    }

    fn pivot(tableau: &mut [Vec<isize>], row: &usize, col: &usize) {
        debug!("PIVOT row: {:?}, col: {:?}", row, col);
        // Make tableau[row][col] = 1 and all other entries in column = 0

        let pivot_element = tableau[*row][*col];
        debug_assert_eq!(pivot_element, 1);

        // In general this should be a float division but since our vectors are all
        // binary (1s and 0s) this is a noop
        //for j in 0..num_columns:
        //    tableau[row][j] /= pivot_element

        // Eliminate other rows
        for i in 0..tableau.len() {
            if i != *row {
                let multiplier = tableau[i][*col];

                for j in 0..tableau[*row].len() {
                    tableau[i][j] -= multiplier * tableau[*row][j];
                }
            }
        }
    }

    fn parse(line: &str, part: Part) -> (Vec<usize>, Vec<Vec<usize>>) {
        debug!("{}", line);
        let mut line_iter = line.trim().chars();
        // First char is a [
        line_iter.next();

        // Next batch of characters is our target
        let mut target: Vec<usize> = Vec::new();
        for (i, c) in line_iter.by_ref().enumerate() {
            match c {
                '.' => (),
                '#' => target.push(i),
                ']' => break,
                _ => panic!("Unexpected char {}", c),
            }
        }

        // Skip a space
        line_iter.next();

        let mut transition_idx_vecs = Vec::new();
        let mut this_transition_idx_vec = Vec::new();
        let mut buffer = String::new();
        for c in line_iter.by_ref() {
            match c {
                ' ' => (),
                '(' => (),
                d if d.is_ascii_digit() => buffer.push(d),
                ',' => {
                    this_transition_idx_vec.push(buffer.parse::<usize>().unwrap());
                    buffer.clear()
                }
                ')' => {
                    this_transition_idx_vec.push(buffer.parse::<usize>().unwrap());
                    transition_idx_vecs.push(this_transition_idx_vec.clone());
                    this_transition_idx_vec.clear();
                    buffer.clear();
                }
                '{' => break,
                _ => panic!("Unexpected char {}", c),
            }
            // debug!(" c {} buffer {} current {}", c, buffer, current);
        }

        // Now parse out the targets for part 2
        let target = if part == Part::Two {
            let mut part2_target = Vec::new();
            buffer.clear();

            for c in line_iter.by_ref() {
                match c {
                    d if d.is_ascii_digit() => buffer.push(d),
                    ',' => {
                        part2_target.push(buffer.parse::<usize>().unwrap());
                        buffer.clear();
                    }
                    '}' => {
                        part2_target.push(buffer.parse::<usize>().unwrap());
                        buffer.clear();
                        break;
                    }
                    _ => panic!("Unexpected char {}", c),
                }
                // debug!(" c {} buffer {} current {}", c, buffer, current);
            }
            part2_target
        } else {
            target
        };

        debug!(
            " target: {:?}, transitions: {:?}",
            target, transition_idx_vecs
        );

        (target, transition_idx_vecs)
    }
}

crate::solver_tests!(Day10, #[ignore]);
