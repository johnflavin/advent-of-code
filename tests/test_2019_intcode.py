from aoc.aoc2019.intcode import Intcode


def test_opcode1():
    ic = Intcode([1, 0, 0, 0, 99])
    ic.run()
    assert ic.memory == [2, 0, 0, 0, 99]


def test_opcode2():
    ic = Intcode([2, 3, 0, 3, 99])
    ic.run()
    assert ic.memory == [2, 3, 0, 6, 99]

    ic = Intcode([2, 4, 4, 5, 99, 0])
    ic.run()
    assert ic.memory == [2, 4, 4, 5, 99, 9801]
