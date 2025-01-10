import random

import pytest

from aoc.aoc2019.intcode import Intcode, run_amplifiers


def test_add():
    program = list(map(int, "1,0,0,0,99".split(",")))
    ic = Intcode(program)
    ic.run()
    assert ic.memory == [2, 0, 0, 0, 99]


def test_multiply():
    program = list(map(int, "2,3,0,3,99".split(",")))
    ic = Intcode(program)
    ic.run()
    assert ic.memory == [2, 3, 0, 6, 99]

    program = list(map(int, "2,4,4,5,99,0".split(",")))
    ic = Intcode(program)
    ic.run()
    assert ic.memory == [2, 4, 4, 5, 99, 9801]


def test_opcode3_4():
    """Outputs whatever it gets as input"""
    program = list(map(int, "3,0,4,0,99".split(",")))
    ic = Intcode(program)
    random_val = random.randint(0, 1024)
    ic.run(random_val)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == random_val


def test_param_mode():
    program = list(map(int, "1002,4,3,4,33".split(",")))
    ic = Intcode(program)
    ic.run()
    assert ic.memory == [1002, 4, 3, 4, 99]


def test_jump_position_mode():
    """Take an input, output 0 if input was 0 or 1 if input was non-zero"""
    program = list(map(int, "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9".split(",")))
    ic = Intcode(program)
    ic.run(0)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 0

    ic = Intcode(program)
    ic.run(random.randint(1, 100))
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 1


def test_jump_immediate_mode():
    """Take an input, output 0 if input was 0 or 1 if input was non-zero"""
    program = list(map(int, "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9".split(",")))
    ic = Intcode(program)
    ic.run(0)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 0

    ic = Intcode(program)
    ic.run(random.randint(1, 100))
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 1


def test_equals_position_mode():
    """Using position mode, consider whether the input
    is equal to 8; output 1 (if it is) or 0 (if it is not)."""
    program = list(map(int, "3,9,8,9,10,9,4,9,99,-1,8".split(",")))

    ic = Intcode(program)
    ic.run(1)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 0

    ic = Intcode(program)
    ic.run(8)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 1


def test_equals_immediate_mode():
    """UUsing immediate mode, consider whether the input
    is equal to 8; output 1 (if it is) or 0 (if it is not)."""
    program = list(map(int, "3,3,1108,-1,8,3,4,3,99".split(",")))

    ic = Intcode(program)
    ic.run(1)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 0

    ic = Intcode(program)
    ic.run(8)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 1


def test_less_than_position_mode():
    """Using position mode, consider whether the input
    is less than 8; output 1 (if it is) or 0 (if it is not)."""
    program = list(map(int, "3,9,7,9,10,9,4,9,99,-1,8".split(",")))

    ic = Intcode(program)
    ic.run(1)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 1

    ic = Intcode(program)
    ic.run(8)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 0


def test_less_than_immediate_mode():
    """Using immediate mode, consider whether the input
    is less than 8; output 1 (if it is) or 0 (if it is not)."""
    program = list(map(int, "3,3,1107,-1,8,3,4,3,99".split(",")))

    ic = Intcode(program)
    ic.run(1)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 1

    ic = Intcode(program)
    ic.run(8)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 0


def test_less_greater_equals_8():
    """The example program uses an input instruction to ask for a single number.
    The program will then output 999 if the input value is below 8,
    output 1000 if the input value is equal to 8,
    or output 1001 if the input value is greater than 8."""
    program_str = (
        "3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,"
        "1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,"
        "999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99"
    )
    program = list(map(int, program_str.split(",")))

    ic = Intcode(program)
    ic.run(random.randint(-10, 7))
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 999

    ic = Intcode(program)
    ic.run(8)
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 1000

    ic = Intcode(program)
    ic.run(random.randint(9, 100))
    output = ic.outputs
    assert len(output) == 1
    assert output[0] == 1001


@pytest.mark.parametrize(
    "program_str,input_seq,feedback,expected_output",
    (
        (
            "3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0",
            (4, 3, 2, 1, 0),
            False,
            43210,
        ),
        (
            "3,23,3,24,1002,24,10,24,1002,23,-1,23,"
            "101,5,23,23,1,24,23,23,4,23,99,0,0",
            (0, 1, 2, 3, 4),
            False,
            54321,
        ),
        (
            "3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,"
            "1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0",
            (1, 0, 4, 3, 2),
            False,
            65210,
        ),
        (
            "3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,"
            "27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5",
            (9, 8, 7, 6, 5),
            True,
            139629729,
        ),
        (
            "3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,"
            "-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,"
            "53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10",
            (9, 7, 8, 5, 6),
            True,
            18216,
        ),
    ),
)
def test_amplifier_sequence(
    program_str: str, input_seq: tuple[int], feedback: bool, expected_output: int
):
    program = list(map(int, program_str.split(",")))

    assert run_amplifiers(program, input_seq, feedback) == expected_output
