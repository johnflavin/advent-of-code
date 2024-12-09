#!/usr/bin/env python
"""
PART 1
We are given a compact representation of file blocks and free space.
Each char alternates between the length of a file and the length of free
space.
The files get IDs based on their ordering in the input.
Move blocks from the files, starting from the right, to the leftmost
free block.
Then calculate a checksum as sum(file id * block index)

Notes
File id can be derived from the index where it is stored.
They're on the even numbers, so 0 -> 0, 2 -> 1, ...
file id = block idx // 2

PART 2
Only move whole files into gaps.
Start moving from right to left.
Only check once if a file can move.
"""
import itertools
import logging
from collections.abc import Iterable


PART_ONE_EXAMPLE = """\
2333133121414131402
"""
PART_ONE_EXAMPLE_RESULT = 1928
PART_ONE_RESULT = 6344673854800
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 2858
PART_TWO_RESULT = 6360363199987


log = logging.getLogger(__name__)


def part_one(lines: Iterable[str]) -> int:
    block_counts = list(map(int, "".join(lines)))

    cumsum = list(itertools.accumulate(block_counts))
    num_file_blocks = sum(itertools.islice(block_counts, 0, None, 2))

    def order_blocks() -> Iterable[tuple[int, int]]:

        left_block_counts_idx = 0
        for idx in range(num_file_blocks):
            # Update which block we are pointing to
            while idx >= cumsum[left_block_counts_idx]:
                left_block_counts_idx += 1

            if left_block_counts_idx % 2 == 0:
                # We are in a file block. Emit file id and block idx.
                file_id = left_block_counts_idx // 2
            else:
                # We are in a free space.

                # If the rightmost file block has reached zero,
                #  remove it and the next free block.
                while block_counts[-1] == 0:
                    _ = block_counts.pop()
                    _ = block_counts.pop()

                # Find the rightmost file and emit it here
                lbc = len(block_counts)
                file_id = lbc // 2

                # "Move" rightmost file block to this free space.
                # We represent this as number of files in the right block
                #   going down by one.
                block_counts[-1] -= 1

            yield file_id, idx

    return sum(file_id * idx for file_id, idx in order_blocks())


def part_two(lines: Iterable[str]) -> int:
    def debug_log(b: list[list[tuple[int, int]]]) -> None:
        if log.isEnabledFor(logging.DEBUG):
            log.debug(
                "".join(
                    itertools.chain.from_iterable(
                        [str(file_id) if file_id != -1 else "."] * num_files
                        for d in b
                        for file_id, num_files in d
                    )
                )
            )

    # blocks: [(file id, block size)]
    blocks = [
        [(block_idx // 2 if block_idx % 2 == 0 else -1, block_size)]
        for block_idx, block_size in enumerate(map(int, "".join(lines)))
    ]
    debug_log(blocks)

    # Move files from the right (i.e. reversed)
    for right_idx, right in reversed(list(enumerate(blocks))):
        if right_idx % 2 == 1:
            # This is a gap, don't move anything
            continue
        # This list has only one entry: the file
        right_file_id, right_len = right[0]

        # Look for a gap from left to right
        for left_idx, left in enumerate(blocks):
            if left_idx % 2 == 0:
                # This is not a gap. Keep looking.
                continue
            if left_idx > right_idx:
                # No suitable gaps to the left of the file. Stop looking.
                break

            # This list may have multiple entries.
            # The remaining gap will always be the last.
            left_file_id, left_len = left[-1]
            if left_file_id == -1 and left_len >= right_len:
                # This gap is big enough. Put the file into it.

                # Remove existing gap
                _ = left.pop()

                # Write right file into the left gap list
                left.append(right.pop())

                # Add a new smaller gap into the left gap list
                remaining_gap_len = left_len - right_len
                left.append((-1, remaining_gap_len))

                # Write a gap into right list
                # (This has no functional purpose, only for debug logging)
                right.append((-1, right_len))

                debug_log(blocks)

                # We've moved the right file. No need to look anymore.
                break

    next_first_idx = 0
    s = 0
    for d in blocks:
        for file_id, file_len in d:
            if file_id != -1:
                # Progressively simplified:
                # s += sum(
                #   file_id*idx
                #   for idx in range(next_first_index, next_first_index + file_len)
                # )
                # s += sum(file_id*(idx+next_first_index) for idx in range(file_len))
                # s += file_id * sum(idx+next_first_index for idx in range(file_len))
                # s += file_id * (
                #       sum(idx for idx in range(file_len)) + file_len*next_first_index
                # )
                s += file_id * (
                    (file_len * (file_len - 1)) // 2 + file_len * next_first_idx
                )
                # NOTE: Don't do integer division (//) because file_len-1 might be odd.
                #       This can introduce floating-point errors, but for our purposes
                #       it's probably fine.
                # s += file_id * file_len * ((file_len - 1) / 2 + next_first_idx)
            next_first_idx += file_len
    return int(s)
