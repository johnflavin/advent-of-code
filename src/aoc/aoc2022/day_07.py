#!/usr/bin/env python
"""
PART 1
Given a terminal log showing cd and ls commands of a directory tree,
find all directories with sizes <= 100000 and sum them.
This may count file sizes multiple times, as a subdirectory may be under
the limit and its parent under the limit too, and we count both.

PART 2
Find the smallest dir size such that subtracting it from the total used
size is 70000000 - 30000000 = 40000000
"""
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field

PART_ONE_EXAMPLE = """\
$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
"""
PART_ONE_EXAMPLE_RESULT = 95437
PART_ONE_RESULT = 1581595
PART_TWO_EXAMPLE = PART_ONE_EXAMPLE
PART_TWO_EXAMPLE_RESULT = 24933642
PART_TWO_RESULT = 1544176


log = logging.getLogger(__name__)


CASH = "$"
CD = "cd"
LS = "ls"
DIR = "dir"


@dataclass(frozen=True)
class File:
    name: str
    size: int


@dataclass
class Dir:
    name: str
    files: list[File] = field(default_factory=list)
    subdirs: list[str] = field(default_factory=list)
    size: int = 0


def create_dirs(cmd_lines: Iterable[str]) -> dict[str, Dir]:
    dir_stack = []
    dirs = {}

    def exit_dir():
        exiting = dir_stack.pop()
        file_size = sum(f.size for f in exiting.files)
        subdir_size = sum(dirs[d].size for d in exiting.subdirs)
        exiting.size = file_size + subdir_size
        log.debug("# Exiting %s size %d", exiting.name, exiting.size)
        dirs[exiting.name] = exiting

    for line in cmd_lines:
        if not line:
            continue
        log.debug(line)
        parts = line.split()
        if parts[0] == CASH and parts[1] == CD:
            where = parts[2]
            if where == "..":
                exit_dir()
            else:
                dir_name = f"{dir_stack[-1].name}{where}/" if dir_stack else where
                entering = Dir(dir_name)
                dir_stack.append(entering)
        elif parts[0] != CASH:
            current_dir = dir_stack[-1]
            something, name = parts[0], parts[1]
            if something == DIR:
                current_dir.subdirs.append(f"{current_dir.name}{name}/")
            else:
                current_dir.files.append(
                    File(f"{current_dir.name}{name}", int(something))
                )
    while dir_stack:
        exit_dir()

    return dirs


def part_one(lines: Iterable[str]) -> int:

    dirs = create_dirs(lines)
    size_limit = 100000

    return sum(d.size for d in dirs.values() if d.size <= size_limit)


def part_two(lines: Iterable[str]) -> int:
    total_space = 70000000
    unused_space_threshold = 30000000
    used_limit = total_space - unused_space_threshold
    dirs = create_dirs(lines)
    used = dirs["/"].size
    for d in sorted(dirs.values(), key=lambda d: d.size):
        if used - d.size < used_limit:
            return d.size
    return -1
