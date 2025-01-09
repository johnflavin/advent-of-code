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
                """Add"""
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
                """Multiply"""
                p1, p2, p3 = self.memory[param_pointer : param_pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                operand1 = p1 if p1_mode else self.memory[p1]
                operand2 = p2 if p2_mode else self.memory[p2]
                result = operand1 * operand2

                assert p3_mode == 0
                self.memory[p3] = result

                self.pointer += 4
            elif opcode == 3:
                """Store input"""
                p1 = self.memory[param_pointer]
                self.memory[p1] = input_val
                self.pointer += 2
            elif opcode == 4:
                """Output"""
                p1 = self.memory[param_pointer]
                p1_mode = param_modes
                operand1 = p1 if p1_mode else self.memory[p1]
                outputs.append(operand1)
                self.pointer += 2
            elif opcode == 5:
                """Jump if true"""
                p1, p2 = self.memory[param_pointer : param_pointer + 2]
                p2_mode, p1_mode = divmod(param_modes, 10)

                operand1 = p1 if p1_mode else self.memory[p1]
                operand2 = p2 if p2_mode else self.memory[p2]

                if operand1 != 0:
                    # Jump
                    self.pointer = operand2
                else:
                    # No jump, regular increment
                    self.pointer += 3
            elif opcode == 6:
                """Jump if false"""
                p1, p2 = self.memory[param_pointer : param_pointer + 2]
                p2_mode, p1_mode = divmod(param_modes, 10)

                operand1 = p1 if p1_mode else self.memory[p1]
                operand2 = p2 if p2_mode else self.memory[p2]

                if operand1 == 0:
                    # Jump
                    self.pointer = operand2
                else:
                    # No jump, regular increment
                    self.pointer += 3
            elif opcode == 7:
                """Less than"""
                p1, p2, p3 = self.memory[param_pointer : param_pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                operand1 = p1 if p1_mode else self.memory[p1]
                operand2 = p2 if p2_mode else self.memory[p2]

                self.memory[p3] = operand1 < operand2

                self.pointer += 4
            elif opcode == 8:
                """Equals"""
                p1, p2, p3 = self.memory[param_pointer : param_pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                operand1 = p1 if p1_mode else self.memory[p1]
                operand2 = p2 if p2_mode else self.memory[p2]

                self.memory[p3] = operand1 == operand2

                self.pointer += 4

        return tuple(outputs)
