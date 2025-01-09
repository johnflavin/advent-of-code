from typing import Iterable


class Intcode:
    memory: list[int]
    pointer: int = 0

    def __init__(self, program: Iterable[int]):
        self.memory = list(program)

    def run(self, input_val: int = 0) -> tuple[int, ...]:
        outputs = []
        while (instruction := self.memory[self.pointer]) != 99:
            param_modes, opcode = divmod(instruction, 100)

            param_pointer = self.pointer + 1
            if opcode == 1:
                p1, p2, p3 = self.memory[param_pointer : param_pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                operand1 = p1 if p1_mode else self.memory[p1]
                operand2 = p2 if p2_mode else self.memory[p2]
                result = operand1 + operand2

                assert p3_mode == 0
                self.memory[p3] = result

                self.pointer += 4
            elif opcode == 2:
                p1, p2, p3 = self.memory[param_pointer : param_pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                operand1 = p1 if p1_mode else self.memory[p1]
                operand2 = p2 if p2_mode else self.memory[p2]
                result = operand1 * operand2

                assert p3_mode == 0
                self.memory[p3] = result

                self.pointer += 4

        return tuple(outputs)
