use crate::solver::Solver;
use anyhow::Result;
use log::debug;

pub struct Day09;

type Int = usize;
type Vec2 = (Int, Int);

impl Solver for Day09 {
    fn year(&self) -> u16 {
        2025
    }

    fn day(&self) -> u8 {
        9
    }

    fn part1_example(&self) -> &str {
        "\
7,1
11,1
11,7
9,7
9,5
2,5
2,3
7,3"
    }

    fn part2_example(&self) -> &str {
        self.part1_example()
    }

    fn part1_example_result(&self) -> Option<&str> {
        Some("50")
    }

    fn part2_example_result(&self) -> Option<&str> {
        Some("24")
    }

    fn part1_result(&self) -> Option<&str> {
        Some("4729332959")
    }

    fn part2_result(&self) -> Option<&str> {
        Some("1474477524")
    }

    fn part1(&self, _input: &str) -> Result<String> {
        // Read in list of node XYZ positions
        let nodes = Self::parse(_input);

        let max_area = nodes
            .iter()
            .enumerate()
            .fold(0usize, |max_area, (i, (ix, iy))| {
                nodes
                    .iter()
                    .skip(i + 1)
                    .fold(max_area, |inner_max_area, (jx, jy)| {
                        debug!("({}, {}) ({}, {})", ix, iy, jx, jy);
                        let (xmin, xmax) = if ix > jx { (*jx, *ix) } else { (*ix, *jx) };
                        let (ymin, ymax) = if iy > jy { (*jy, *iy) } else { (*iy, *jy) };
                        let area = (xmax + 1 - xmin) * (ymax + 1 - ymin);
                        inner_max_area.max(area)
                    })
            });

        Ok(max_area.to_string())
    }

    /**
    Now we can only make a rectangle if it is all "red" or "green"
    I'm going to solve this related problem which I _think_ is equivalent
      For each pair of points, turn them into two ranges: x and y
      If any of the other points are inside both ranges, then the rectangle is invalid
    ...
    This didn't work for a couple reasons
    1. It doesn't have any notion of "inside" and "outside". Two points on the exterior
       can make a rectangle all on the exterior of the shape and we need to discard that.
    2. I'm not able to reliably determine when a node is "inside" the rectangle yet

    I think I may need to flood fill this shape
    Talked to Claude about it. I don't need to flood fill.
    If I want to test if a given point is inside or outside the shape I can do an "even/odd" test.

    No, forget all that. I found a resource that basically tells me exactly how to solve this:
    How to Check if a Rectangle is Inside Another Polygon Using Two Coordinates: From Point-in-Polygon to Polygon Containment
    https://www.xjavascript.com/blog/check-if-polygon-is-inside-a-polygon/

    Steps for a rectangle
    - Derive the four corners: minx miny, minx maxy, maxx miny, maxx maxy
    - Use a ray-casting algorithm to check that each of these points is in the polygon
      (though first check if each corner = a vertex or is on a segment, because that's faster)
    - Check for any edge intersections. There shouldn't be any. (Other than coincident edges.)
    - That's it! Rectangle is inside if all vertices are inside and no edges intersect.

    ...

    That didn't work for me either. I just had to go to reddit.
    More or less copied / adapted this solution:
    https://old.reddit.com/r/adventofcode/comments/1phywvn/2025_day_9_solutions/ntwm1yj/
    */
    fn part2(&self, _input: &str) -> Result<String> {
        let nodes = Self::parse(_input);

        let max_area = nodes
            .iter()
            .enumerate()
            .fold(0usize, |max_area, (i, (ix, iy))| {
                nodes
                    .iter()
                    .skip(i + 1)
                    .fold(max_area, |inner_max_area, (jx, jy)| {
                        debug!("({}, {}) ({}, {})", ix, iy, jx, jy);
                        let (xmin, xmax) = if ix > jx { (*jx, *ix) } else { (*ix, *jx) };
                        let (ymin, ymax) = if iy > jy { (*jy, *iy) } else { (*iy, *jy) };

                        // check if the box is entirely within the polygon.
                        if nodes
                            .iter()
                            .zip(nodes.iter().cycle().skip(1).take(nodes.len()))
                            .all(|(&(px, py), &(qx, qy))| {
                                debug!(
                                    "  Checking intersection with ({}, {}) ({}, {})",
                                    px, py, qx, qy
                                );
                                if py == qy {
                                    // Horizontal.
                                    py >= ymax
                                        || py <= ymin
                                        || (px <= xmin && qx <= xmin)
                                        || (px >= xmax && qx >= xmax)
                                } else {
                                    // Vertical.
                                    px >= xmax
                                        || px <= xmin
                                        || (py <= ymin && qy <= ymin)
                                        || (py >= ymax && qy >= ymax)
                                }
                            })
                        {
                            inner_max_area.max((xmax + 1 - xmin) * (ymax + 1 - ymin))
                        } else {
                            inner_max_area
                        }
                    })
            });

        Ok(max_area.to_string())
    }
}

impl Day09 {
    fn parse(_input: &str) -> Vec<Vec2> {
        // Read in list of node XYZ positions
        _input
            .trim()
            .lines()
            .map(|line| {
                let (x, y) = line
                    .trim()
                    .split_once(',')
                    .expect("Cannot read coordinates");
                (
                    x.parse::<Int>().expect("Cannot parse"),
                    y.parse::<Int>().expect("Cannot parse"),
                )
            })
            .collect::<Vec<_>>()
    }
}

crate::solver_tests!(Day09);
