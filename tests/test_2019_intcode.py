import random

from aoc.aoc2019.intcode import Intcode


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
    output = ic.run(random_val)
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
    output = ic.run(0)
    assert len(output) == 1
    assert output[0] == 0

    ic = Intcode(program)
    output = ic.run(random.randint(1, 100))
    assert len(output) == 1
    assert output[0] == 1


def test_jump_immediate_mode():
    """Take an input, output 0 if input was 0 or 1 if input was non-zero"""
    program = list(map(int, "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9".split(",")))
    ic = Intcode(program)
    output = ic.run(0)
    assert len(output) == 1
    assert output[0] == 0

    ic = Intcode(program)
    output = ic.run(random.randint(1, 100))
    assert len(output) == 1
    assert output[0] == 1


def test_equals_position_mode():
    """Using position mode, consider whether the input
    is equal to 8; output 1 (if it is) or 0 (if it is not)."""
    program = list(map(int, "3,9,8,9,10,9,4,9,99,-1,8".split(",")))

    ic = Intcode(program)
    output = ic.run(1)
    assert len(output) == 1
    assert output[0] == 0

    ic = Intcode(program)
    output = ic.run(8)
    assert len(output) == 1
    assert output[0] == 1


def test_equals_immediate_mode():
    """UUsing immediate mode, consider whether the input
    is equal to 8; output 1 (if it is) or 0 (if it is not)."""
    program = list(map(int, "3,3,1108,-1,8,3,4,3,99".split(",")))

    ic = Intcode(program)
    output = ic.run(1)
    assert len(output) == 1
    assert output[0] == 0

    ic = Intcode(program)
    output = ic.run(8)
    assert len(output) == 1
    assert output[0] == 1


def test_less_than_position_mode():
    """Using position mode, consider whether the input
    is less than 8; output 1 (if it is) or 0 (if it is not)."""
    program = list(map(int, "3,9,7,9,10,9,4,9,99,-1,8".split(",")))

    ic = Intcode(program)
    output = ic.run(1)
    assert len(output) == 1
    assert output[0] == 1

    ic = Intcode(program)
    output = ic.run(8)
    assert len(output) == 1
    assert output[0] == 0


def test_less_than_immediate_mode():
    """Using immediate mode, consider whether the input
    is less than 8; output 1 (if it is) or 0 (if it is not)."""
    program = list(map(int, "3,3,1107,-1,8,3,4,3,99".split(",")))

    ic = Intcode(program)
    output = ic.run(1)
    assert len(output) == 1
    assert output[0] == 1

    ic = Intcode(program)
    output = ic.run(8)
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
    output = ic.run(random.randint(-10, 7))
    assert len(output) == 1
    assert output[0] == 999

    ic = Intcode(program)
    output = ic.run(8)
    assert len(output) == 1
    assert output[0] == 1000

    ic = Intcode(program)
    output = ic.run(random.randint(9, 100))
    assert len(output) == 1
    assert output[0] == 1001
