use crate::solver::Solver;
use anyhow::Result;
use log::debug;
use std::cmp::{max, min};
use std::collections::HashMap;

pub struct Day08;

type Vec3 = (u64, u64, u64);
type Vec3s = Vec<Vec3>;
type NodeDists = (u64, Vec3, Vec3);

impl Solver for Day08 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        8
    }

    fn part1_example(&self) -> &str {
        "\
162,817,812
57,618,57
906,360,560
592,479,940
352,342,300
466,668,158
542,29,236
431,825,988
739,650,466
52,470,668
216,146,977
819,987,18
117,168,530
805,96,715
346,949,466
970,615,88
941,993,340
862,61,35
984,92,344
425,690,689"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("40")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("25272")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("123420")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("673096646")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        let (mut node_to_circuit_id, mut circuit_id_to_nodes, distances_sq) =
            Self::parse_and_prep(_input);

        // We have a different number of nodes to move if we're in the example or actual input
        let num_to_move = if _input.eq(self.part1_example()) {
            10
        } else {
            1000
        };

        // Loop over distances (shortest 10)
        for (_, node_a, node_b) in distances_sq.iter().take(num_to_move) {
            Self::connect_nodes(
                &mut node_to_circuit_id,
                &mut circuit_id_to_nodes,
                node_a,
                node_b,
            );
        }

        // Sort circuit map values by vec len
        let mut circuit_lens = circuit_id_to_nodes
            .values()
            .map(|v| v.len() as u64)
            .collect::<Vec<_>>();
        circuit_lens.sort_by(|a, b| b.cmp(a)); // Reverse sort to get largest first
        debug!("circuit_lens: {:?}", circuit_lens);

        // Answer is product of 3 longest lengths
        Ok(circuit_lens[..3].iter().product::<u64>().to_string())
    }

    fn part2(&self, _input: &str) -> Result<String> {
        let (mut node_to_circuit_id, mut circuit_id_to_nodes, distances_sq) =
            Self::parse_and_prep(_input);

        // Loop over distances until all are connected
        let mut dist_iter = distances_sq.iter();
        let answer = loop {
            let (_, node_a, node_b) = dist_iter.next().unwrap();
            Self::connect_nodes(
                &mut node_to_circuit_id,
                &mut circuit_id_to_nodes,
                node_a,
                node_b,
            );

            // Stop when there is a single circuit
            if circuit_id_to_nodes.len() == 1 {
                // Answer is x coords multiplied together
                break node_a.0 * node_b.0;
            }
        };

        Ok(answer.to_string())
    }
}

impl Day08 {
    fn parse_and_prep(
        _input: &str,
    ) -> (HashMap<Vec3, usize>, HashMap<usize, Vec3s>, Vec<NodeDists>) {
        // Read in list of node XYZ positions
        let nodes = _input
            .trim()
            .lines()
            .map(|line| {
                let mut xyz_iter = line.split(",").map(|s| s.parse::<u64>().unwrap());
                (
                    xyz_iter.next().unwrap(),
                    xyz_iter.next().unwrap(),
                    xyz_iter.next().unwrap(),
                )
            })
            .collect::<Vec<_>>();

        // Make map of node: circuit ID (start with incrementing int)
        // Make map of circuit ID to vec of nodes (start with single-node vecs)
        let mut node_to_circuit_id = HashMap::new();
        let mut circuit_id_to_nodes = HashMap::new();
        for (i, &node) in nodes.iter().enumerate() {
            node_to_circuit_id.insert(node, i);
            circuit_id_to_nodes.insert(i, vec![node]);
        }

        // Calculate node-pair distances
        let mut distances_sq = Vec::new();
        for (i, &node_a) in nodes.iter().enumerate() {
            for &node_b in nodes.iter().skip(i + 1) {
                distances_sq.push((
                    (max(node_a.0, node_b.0) - min(node_a.0, node_b.0)).pow(2)
                        + (max(node_a.1, node_b.1) - min(node_a.1, node_b.1)).pow(2)
                        + (max(node_a.2, node_b.2) - min(node_a.2, node_b.2)).pow(2),
                    min(node_a, node_b),
                    max(node_b, node_a),
                ));
            }
        }
        // Sort distances
        distances_sq.sort();
        (node_to_circuit_id, circuit_id_to_nodes, distances_sq)
    }

    fn connect_nodes(
        node_to_circuit_id: &mut HashMap<Vec3, usize>,
        circuit_id_to_nodes: &mut HashMap<usize, Vec3s>,
        node_a: &Vec3,
        node_b: &Vec3,
    ) {
        // Find current circuits for both nodes (A and B)
        let circuit_id_a = node_to_circuit_id[node_a];
        let circuit_id_b = node_to_circuit_id[node_b];
        if circuit_id_a == circuit_id_b {
            // They're already in the same circuit
            debug!(
                "node_a: {:?}, node_b: {:?} already in same circuit {}",
                node_a, node_b, circuit_id_a
            );
            return;
        }
        // Look up node lists for circuits A and B (remove instead of get so we don't immutably borrow)
        let mut circuit_a = circuit_id_to_nodes.remove(&circuit_id_a).unwrap();
        let circuit_b = circuit_id_to_nodes.remove(&circuit_id_b).unwrap();
        debug!(
            "Moving {} nodes from circuit {} to circuit {} (size {} -> {})",
            circuit_b.len(),
            circuit_id_b,
            circuit_id_a,
            circuit_a.len(),
            circuit_a.len() + circuit_b.len()
        );
        // In circuit map: Put all B nodes into A. Reinsert A to map.
        circuit_a.extend(circuit_b.clone());
        circuit_id_to_nodes.insert(circuit_id_a, circuit_a);

        // In node map: assign circuit ID A to all B nodes
        for node_b in circuit_b {
            node_to_circuit_id.insert(node_b, circuit_id_a);
        }
    }
}

crate::solver_tests!(Day08);
