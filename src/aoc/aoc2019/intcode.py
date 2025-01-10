from typing import Iterable


class Intcode:
    memory: list[int]
    pointer: int = 0
    outputs: list[int]
    is_halted: bool = False

    def __init__(self, program: Iterable[int]):
        self.memory = list(program)
        self.outputs = []

    def run(self, input_: int | None = None) -> None:
        while not self.is_halted:
            instruction = self.memory[self.pointer]
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

                if input_ is None:
                    break
                self.memory[p1] = input_
                input_ = None
                self.pointer += 2
            elif opcode == 4:
                """Output"""
                p1 = self.memory[param_pointer]
                p1_mode = param_modes
                operand1 = p1 if p1_mode else self.memory[p1]
                self.outputs.append(operand1)
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
            elif opcode == 99:
                self.is_halted = True


def run_amplifiers(
    program: Iterable[int], input_seq: tuple[int, ...], feedback: bool
) -> int:
    num_amplifiers = len(input_seq)

    # Start all ics with the same program
    ics = [Intcode(program) for _ in range(num_amplifiers)]

    # Feed the sequence into each
    for i, ic in zip(input_seq, ics):
        ic.run(i)

    # Start the process by feeding 0 into the first
    input0 = 0
    while not ics[-1].is_halted:
        ics[0].run(input0)

        # Hook the output of one into the input of the next
        for i in range(1, num_amplifiers):
            ics[i].run(ics[i - 1].outputs[-1])

        if feedback:
            # Feed final output back to first and keep going
            input0 = ics[-1].outputs[-1]
        else:
            break

    # Final output
    return ics[-1].outputs[-1]
