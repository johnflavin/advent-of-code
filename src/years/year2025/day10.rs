use crate::solver::{Part, Solver};
use anyhow::Result;
use log::debug;
use num_rational::Ratio;
use std::collections::{HashSet, VecDeque};

pub struct Day10;

enum SimplexResult {
    Infeasible,
    Unbounded,
    Optimal(Vec<Ratio<isize>>),
}

impl Solver for Day10 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        10
    }

    fn part1_example(&self) -> &str {
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
        Some("18273")
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
            let part1 = Self::solve_part1(target, &transitions);
            debug!("Solution: {}", part1);
            total + part1
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
            let part2 = Self::solve_part2(&target, &basis);
            debug!("Solution: {}", part2);
            total + part2
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
        debug!("BEGIN PART 2: target {:?} vectors {:?}", target, vectors);

        // let result = Self::solve_lp(
        //     ,
        //     vectors,
        //     &vec![Ratio::ZERO; n],
        //     &vec![None; n]
        // );

        let n = vectors.len();

        // Initial bounds: all variables >= 0, no upper bounds
        let lower_bounds = vec![0; n];
        let upper_bounds = vec![None; n];
        let mut best_so_far = None;

        let result = Self::solve_with_branch_and_bound(
            &target.iter().map(|&t| t as isize).collect::<Vec<_>>(),
            vectors,
            &lower_bounds,
            &upper_bounds,
            &mut best_so_far,
            n,
        );

        result.expect("No solution found")
    }

    fn solve_with_branch_and_bound(
        target: &[isize],
        vectors: &[Vec<usize>],
        lower_bounds: &Vec<isize>,
        upper_bounds: &Vec<Option<isize>>,
        best_so_far: &mut Option<Ratio<isize>>, // for pruning
        n: usize,
    ) -> Option<usize> {
        match Self::solve_lp(target, vectors, lower_bounds, upper_bounds) {
            SimplexResult::Infeasible => None,
            SimplexResult::Unbounded => panic!("shouldn't happen for this problem"),
            SimplexResult::Optimal(solution) => {
                let objective = solution.iter().take(n).sum::<Ratio<isize>>();

                // Prune if worse than best known
                if best_so_far.is_some_and(|best| objective >= best) {
                    return None;
                }

                // Check if integral
                if let Some(fractional_idx) = Self::find_fractional_variable(&solution) {
                    let frac_val = solution[fractional_idx];

                    // Branch down: x_i <= floor(frac_val)
                    let mut upper_branch = upper_bounds.clone();
                    upper_branch[fractional_idx] = Some(*frac_val.floor().numer());
                    debug!(
                        " Branch idx {} upper {:?} ",
                        fractional_idx,
                        frac_val.floor()
                    );
                    let down = Self::solve_with_branch_and_bound(
                        target,
                        vectors,
                        lower_bounds,
                        &upper_branch,
                        best_so_far,
                        n,
                    );

                    // Branch up: x_i >= ceil(frac_val)
                    let mut lower_branch = lower_bounds.clone();
                    lower_branch[fractional_idx] = *frac_val.ceil().numer();
                    debug!(
                        " Branch idx {} lower {:?} ",
                        fractional_idx,
                        frac_val.ceil()
                    );
                    let up = Self::solve_with_branch_and_bound(
                        target,
                        vectors,
                        &lower_branch,
                        upper_bounds,
                        best_so_far,
                        n,
                    );

                    // Return better of the two
                    match (down, up) {
                        (Some(d), Some(u)) => Some(d.min(u)),
                        (d, u) => d.or(u),
                    }
                } else {
                    // Solution is integral!
                    if best_so_far.is_none_or(|best| objective < best) {
                        *best_so_far = Some(objective);
                    }
                    Some(objective.to_integer() as usize)
                }
            }
        }
    }

    fn solve_lp(
        target: &[isize],
        vectors: &[Vec<usize>],
        lower_bounds: &[isize],         // defaults to all zeros
        upper_bounds: &[Option<isize>], // None = unbounded
    ) -> SimplexResult {
        debug!(
            "BEGIN Solution: target {:?} vectors {:?} lower_bounds {:?} upper_bounds {:?}",
            target, vectors, lower_bounds, upper_bounds
        );

        let num_variables = vectors.len();
        let num_artificial = target.len();
        let mut num_upper_bound_slacks = 0;

        let mut num_rows = num_artificial;
        let mut num_cols = num_variables + num_artificial + 1;

        // Arrange vectors into columns of matrix A
        let mut a = (0..num_rows).map(|_| vec![]).collect::<Vec<_>>();
        for v in vectors {
            for (item, a_row) in v.iter().zip(&mut a) {
                a_row.push(item);
            }
        }

        // Find initial feasible solution
        let mut basis = (0..num_artificial)
            .map(|i| num_variables + i)
            .collect::<Vec<_>>();

        // Create extended tableau with artificial variables
        // [A | I | b] where I is d×d identity for artificial vars
        let mut tableau: Vec<Vec<Ratio<isize>>> = Vec::with_capacity(num_rows);
        // debug!("initial tableau:");
        for (i, &t) in target.iter().enumerate() {
            let mut tableau_row = vec![Ratio::ZERO; num_cols];
            // A
            (0..num_variables).for_each(|j| tableau_row[j] = Ratio::new(vectors[j][i] as isize, 1));
            // Identity matrix representing artifical variables
            tableau_row[num_variables + i] = Ratio::ONE;
            // b
            tableau_row[num_variables + num_artificial] = Ratio::new(t, 1);

            // debug!(" {:?}", tableau_row);
            tableau.push(tableau_row);
        }

        // Modify tableau for upper bounds
        // If an upper bound i exists, add a row with 1 in column i,
        //   an additional slack variable with 1, and the bound value as the target
        for (i, &u) in upper_bounds.iter().enumerate() {
            if let Some(u) = u {
                // First slide over all target values by one col
                for row in tableau.iter_mut() {
                    let target = row.pop().unwrap();
                    row.push(Ratio::ZERO);
                    row.push(target);
                }

                // Next add new row with a 1 in variable i, 1 in new slack var, and u in target
                let mut new_row = vec![Ratio::ZERO; num_cols + 1];
                new_row[i] = Ratio::ONE;
                new_row[num_cols - 1] = Ratio::ONE;
                new_row[num_cols] = Ratio::new(u, 1);

                tableau.push(new_row);

                // Add new slack variable to basis
                basis.push(num_cols - 1);

                // Now update the tableau size
                num_cols += 1;
                num_rows += 1;
                num_upper_bound_slacks += 1;
            }
        }

        // Modify tableau for lower bounds
        for (i, &l) in lower_bounds.iter().enumerate() {
            if l > 0 {
                // We know that vector xi must be in the solution at least l times
                // So let's just take that into account by lowering the target values by l*xi
                // Then later once we find a solution we'll add l back into it
                let xi = tableau.iter().map(|row| row[i]).collect::<Vec<_>>();
                for (j, row) in tableau.iter_mut().enumerate() {
                    row[num_cols - 1] -= xi[j] * l;
                }
            }
        }

        // Phase 1 cost: 0 for all real variables, 1 for fake variables
        let phase1_cost = [
            vec![0; num_variables],
            vec![1; num_artificial],
            vec![0; num_upper_bound_slacks],
        ]
        .concat();

        // Find entering variable (most negative reduced cost)
        while let Some(entering) = Self::find_entering(&tableau, &phase1_cost, &basis, num_cols) {
            // Find leaving variable (minimum ratio test)
            let leaving_opt = Self::find_leaving(&tableau, entering, num_cols);
            if Option::is_none(&leaving_opt) {
                panic!("unbounded");
            }
            let leaving = leaving_opt.unwrap();

            Self::pivot(&mut tableau, leaving, entering, num_rows, num_cols);

            basis[leaving] = entering;

            // debug!(" {:?}", tableau);
        }

        // Check if feasible (all artificial variables should be zero)
        debug!("End of phase 1. Basis: {:?}", basis);
        if basis.iter().enumerate().any(|(i, &x)| {
            x >= num_variables
                && x < num_variables + num_artificial
                && tableau[i][num_cols - 1] != Ratio::ZERO
        }) {
            return SimplexResult::Infeasible;
        }

        // Remove artificial variables from basis
        for row_idx in 0..num_rows {
            let basis_var = basis[row_idx];
            if basis_var >= num_variables && basis_var < num_variables + num_artificial {
                // Artificial variable in basis - try to pivot it out
                // Find any original variable with non-zero coefficient in this row
                for col in 0..num_variables {
                    if tableau[row_idx][col] != Ratio::ZERO {
                        // Pivot: artificial leaves, original enters
                        Self::pivot(&mut tableau, row_idx, col, num_rows, num_cols);
                        basis[row_idx] = col;
                        break;
                    }
                }
                // If no pivot found, the row is redundant (all original var coefficients are 0)
                // You could remove the row or just leave the artificial variable
            }
        }

        // Optimize actual objective (sum of coefficients)

        // Phase 2 cost: 1 for all real variables, 0 for fake variables
        let phase2_cost = [
            vec![1; num_variables],
            vec![0; num_artificial],
            vec![0; num_upper_bound_slacks],
        ]
        .concat();

        while let Some(entering) =
            Self::find_entering(&tableau, &phase2_cost, &basis, num_variables)
        {
            // Find leaving variable (minimum ratio test)
            let leaving_opt = Self::find_leaving(&tableau, entering, num_cols);
            if Option::is_none(&leaving_opt) {
                return SimplexResult::Unbounded;
            }
            let leaving = leaving_opt.unwrap();

            Self::pivot(&mut tableau, leaving, entering, num_rows, num_cols);

            basis[leaving] = entering;

            // debug!(" {:?}", tableau);
        }

        debug!("End of phase 2. Basis: {:?}", basis);

        // Add back lower bound values that we removed earlier
        let mut solution = lower_bounds
            .iter()
            .map(|&l| Ratio::new(l, 1))
            .collect::<Vec<_>>();
        for (row_idx, &basis_var) in basis.iter().enumerate() {
            if basis_var < num_variables {
                solution[basis_var] += tableau[row_idx][num_cols - 1];
            }
        }
        debug!("solution: {:?}", solution);

        let mut check = vec![Ratio::ZERO; target.len()];
        for (var_idx, &val) in solution.iter().enumerate() {
            for (row_idx, &coef) in vectors[var_idx].iter().enumerate() {
                check[row_idx] += val * Ratio::new(coef as isize, 1);
            }
        }
        debug!("A*x = {:?}, target = {:?}", check, target);
        debug_assert_eq!(
            check.iter().map(|&r| *r.numer()).collect::<Vec<_>>(),
            target
        );

        SimplexResult::Optimal(solution)
    }

    fn find_entering(
        tableau: &[Vec<Ratio<isize>>],
        cost: &[isize],
        basis: &[usize],
        num_cols: usize,
    ) -> Option<usize> {
        // Compute reduced costs for non-basic variables
        // reduced_cost[j] = c[j] - basis_cost^T * A[j]

        let mut min_reduced_cost = Ratio::ZERO;
        let mut entering = None;

        for j in 0..(num_cols - 1) {
            if basis.contains(&j) {
                continue;
            }

            // Compute reduced cost
            let mut reduced_cost = Ratio::new(cost[j], 1);
            for (i, &basis_var) in basis.iter().enumerate() {
                reduced_cost -= Ratio::new(cost[basis_var], 1) * tableau[i][j];
            }

            if reduced_cost < min_reduced_cost {
                min_reduced_cost = reduced_cost;
                entering = Some(j);
            }
        }

        entering
    }

    fn find_leaving(
        tableau: &[Vec<Ratio<isize>>],
        entering_col: usize,
        num_cols: usize,
    ) -> Option<usize> {
        // Minimum ratio test: min(b[i] / A[i][entering]) for A[i][entering] > 0

        let mut min_ratio = None;
        let mut leaving = None;

        for (i, tableau_row) in tableau.iter().enumerate() {
            if tableau_row[entering_col] > Ratio::ZERO {
                let ratio = tableau_row[num_cols - 1] / tableau_row[entering_col];
                if min_ratio.is_none_or(|r| ratio < r) {
                    min_ratio = Some(ratio);
                    leaving = Some(i);
                }
            }
        }

        leaving
    }

    fn pivot(
        tableau: &mut [Vec<Ratio<isize>>],
        row: usize,
        col: usize,
        num_rows: usize,
        num_cols: usize,
    ) {
        debug!("PIVOT row: {:?}, col: {:?}", row, col);

        let pivot_element = tableau[row][col];

        #[allow(clippy::needless_range_loop)]
        for j in 0..num_cols {
            tableau[row][j] /= pivot_element
        }

        // For borrow checker
        let tableau_row_clone = tableau[row].clone();

        // Eliminate other rows
        for (i, tableau_row) in tableau.iter_mut().enumerate().take(num_rows) {
            if i != row {
                let multiplier = tableau_row[col];

                for j in 0..num_cols {
                    tableau_row[j] -= multiplier * tableau_row_clone[j];
                }
            }
        }
    }

    fn find_fractional_variable(solution: &[Ratio<isize>]) -> Option<usize> {
        for (i, r) in solution.iter().enumerate() {
            if !r.is_integer() {
                return Some(i);
            }
        }
        None
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

        (target, transition_idx_vecs)
    }
}

crate::solver_tests!(Day10);
