use num_traits::PrimInt;
use std::cmp::{max, min};
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Range<T: PrimInt> {
    pub start: T,
    pub end: T,
}

impl<T: PrimInt> Range<T> {
    pub fn new(start: T, end: T) -> Self {
        Range { start, end }
    }

    /// Check if this range overlaps with another
    pub fn overlaps(&self, other: &Range<T>) -> bool {
        self.start <= other.end && other.start <= self.end
    }

    /// Get the union if ranges overlap, otherwise None
    pub fn union(&self, other: &Range<T>) -> Option<Range<T>> {
        if self.overlaps(other) {
            Some(Range {
                start: *min(&self.start, &other.start),
                end: *max(&self.end, &other.end),
            })
        } else {
            None
        }
    }

    /// Get the intersection if ranges overlap, otherwise None
    pub fn intersection(&self, other: &Range<T>) -> Option<Range<T>> {
        if self.overlaps(other) {
            Some(Range {
                start: *max(&self.start, &other.start),
                end: *min(&self.end, &other.end),
            })
        } else {
            None
        }
    }

    /// Check if a value is within this range (inclusive)
    pub fn contains(&self, value: &T) -> bool {
        &self.start <= value && value <= &self.end
    }

    /// Subtract another range from this one, returning 0, 1, or 2 ranges
    pub fn difference(&self, other: &Range<T>) -> Vec<Range<T>> {
        if !self.overlaps(other) {
            // No overlap, return original range
            return vec![*self];
        }

        let mut result = Vec::new();

        // Left piece (before the subtracted range)
        if self.start < other.start {
            result.push(Range {
                start: self.start,
                end: *min(&self.end, &(other.start - T::one())),
            });
        }

        // Right piece (after the subtracted range)
        if self.end > other.end {
            result.push(Range {
                start: *max(&self.start, &(other.end + T::one())),
                end: self.end,
            });
        }

        result
    }
}

impl<T: PrimInt> Range<T> {
    pub fn len(&self) -> T {
        self.end - self.start + T::one()
    }

    pub fn is_empty(&self) -> bool {
        self.start > self.end
    }
}

impl<T: fmt::Display + PrimInt> fmt::Display for Range<T> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}, {}]", self.start, self.end)
    }
}

/// Consolidate overlapping ranges into a minimal set of disjoint ranges
pub fn union<T: PrimInt>(mut ranges: Vec<Range<T>>) -> Vec<Range<T>> {
    if ranges.is_empty() {
        return ranges;
    }

    // Sort by start point
    ranges.sort_by(|a, b| a.start.cmp(&b.start));

    let mut result = Vec::new();
    let mut current = ranges[0];

    for range in ranges.into_iter().skip(1) {
        if let Some(merged) = current.union(&range) {
            current = merged;
        } else {
            result.push(current);
            current = range;
        }
    }
    result.push(current);

    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_overlaps() {
        let r1 = Range::new(1, 5);
        let r2 = Range::new(3, 7);
        let r3 = Range::new(6, 10);

        assert!(r1.overlaps(&r2));
        assert!(!r1.overlaps(&r3));
    }

    #[test]
    fn test_union() {
        let r1 = Range::new(1, 5);
        let r2 = Range::new(3, 7);

        assert_eq!(r1.union(&r2), Some(Range::new(1, 7)));

        let r3 = Range::new(10, 15);
        assert_eq!(r1.union(&r3), None);
    }

    #[test]
    fn test_intersection() {
        let r1 = Range::new(1, 5);
        let r2 = Range::new(3, 7);

        assert_eq!(r1.intersection(&r2), Some(Range::new(3, 5)));

        let r3 = Range::new(10, 15);
        assert_eq!(r1.intersection(&r3), None);
    }

    #[test]
    fn test_difference() {
        let r1 = Range::new(1, 10);
        let r2 = Range::new(4, 6);

        // Subtracting middle creates two ranges
        assert_eq!(
            r1.difference(&r2),
            vec![Range::new(1, 3), Range::new(7, 10)]
        );

        // Subtracting from left
        let r3 = Range::new(1, 5);
        assert_eq!(r1.difference(&r3), vec![Range::new(6, 10)]);

        // No overlap
        let r4 = Range::new(20, 30);
        assert_eq!(r1.difference(&r4), vec![Range::new(1, 10)]);
    }

    #[test]
    fn test_make_disjoint() {
        let ranges = vec![
            Range::new(1, 3),
            Range::new(2, 5),
            Range::new(7, 9),
            Range::new(8, 12),
        ];

        let disjoint = union(ranges);
        assert_eq!(disjoint, vec![Range::new(1, 5), Range::new(7, 12)]);
    }
}
