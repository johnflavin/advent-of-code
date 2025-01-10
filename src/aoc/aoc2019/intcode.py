import logging
from collections import defaultdict
from typing import Iterable


log = logging.getLogger(__name__)
is_debug = log.isEnabledFor(logging.DEBUG)


class Intcode:
    mem: dict[int, int]
    pointer: int = 0
    outputs: list[int]
    is_halted: bool = False
    relative_base: int = 0

    def __init__(self, program: Iterable[int]):
        self.mem = defaultdict(int)
        self.mem.update(enumerate(program))
        self.outputs = []

    @property
    def memory(self) -> list[int]:
        """Output memory as a list rather than a dict"""
        max_key = max(self.mem.keys())
        memory = [0] * (max_key + 1)
        for i, val in self.mem.items():
            memory[i] = val
        return memory

    def operand(self, value: int, mode: int):
        if mode == 1:
            result = value
            log.debug(" + P %d M %d -> %d", value, mode, result)
        else:
            mem_pointer = self.mem_pointer(value, mode)
            result = self.mem[mem_pointer]
            log.debug(
                " + P %d M %d -> self.mem[%d] = %d", value, mode, mem_pointer, result
            )

        return result

    def mem_pointer(self, value: int, mode: int) -> int:
        mem_pointer = value + (self.relative_base if mode == 2 else 0)
        log.debug(" + P %d M %d -> %d", value, mode, mem_pointer)
        return mem_pointer

    def run(self, input_: int | None = None) -> None:
        while not self.is_halted:
            instruction = self.mem[self.pointer]
            param_modes, opcode = divmod(instruction, 100)
            log.debug("--- Instruction %d ---", instruction)

            if opcode == 1:
                """Add"""
                p1 = self.mem[self.pointer + 1]
                p2 = self.mem[self.pointer + 2]
                p3 = self.mem[self.pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                op1 = self.operand(p1, p1_mode)
                op2 = self.operand(p2, p2_mode)
                result = op1 + op2

                mem_pointer = self.mem_pointer(p3, p3_mode)
                self.mem[mem_pointer] = result
                log.debug("OC%d Storing %d to mem[%d]", opcode, result, mem_pointer)

                self.pointer += 4
            elif opcode == 2:
                """Multiply"""
                p1 = self.mem[self.pointer + 1]
                p2 = self.mem[self.pointer + 2]
                p3 = self.mem[self.pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                op1 = self.operand(p1, p1_mode)
                op2 = self.operand(p2, p2_mode)
                result = op1 * op2

                mem_pointer = self.mem_pointer(p3, p3_mode)
                self.mem[mem_pointer] = result
                log.debug("OC%d Storing %d to mem[%d]", opcode, result, mem_pointer)

                self.pointer += 4
            elif opcode == 3:
                """Store input"""
                p1 = self.memory[self.pointer + 1]
                param_modes, p1_mode = divmod(param_modes, 10)

                mem_pointer = self.mem_pointer(p1, p1_mode)

                if input_ is None:
                    log.debug("OC%d No input available. Pausing.", opcode)
                    break
                self.mem[mem_pointer] = input_
                log.debug("OC%d Storing %d to %d", opcode, input_, mem_pointer)
                input_ = None
                self.pointer += 2
            elif opcode == 4:
                """Output"""
                p1 = self.mem[self.pointer + 1]

                p1_mode = param_modes
                op1 = self.operand(p1, p1_mode)
                self.outputs.append(op1)
                log.debug("OC%d Outputting %d", opcode, op1)
                self.pointer += 2
            elif opcode == 5:
                """Jump if true"""
                p1 = self.mem[self.pointer + 1]
                p2 = self.mem[self.pointer + 2]

                p2_mode, p1_mode = divmod(param_modes, 10)

                op1 = self.operand(p1, p1_mode)
                op2 = self.operand(p2, p2_mode)

                if op1 != 0:
                    # Jump
                    log.debug("OC%d Jump to %d", opcode, op2)
                    self.pointer = op2
                else:
                    # No jump, regular increment
                    log.debug("OC%d No jump", opcode)
                    self.pointer += 3
            elif opcode == 6:
                """Jump if false"""
                p1 = self.mem[self.pointer + 1]
                p2 = self.mem[self.pointer + 2]

                p2_mode, p1_mode = divmod(param_modes, 10)

                op1 = self.operand(p1, p1_mode)
                op2 = self.operand(p2, p2_mode)

                if op1 == 0:
                    # Jump
                    log.debug("OC%d Jump to %d", opcode, op2)
                    self.pointer = op2
                else:
                    # No jump, regular increment
                    log.debug("OC%d No jump", opcode)
                    self.pointer += 3
            elif opcode == 7:
                """Less than"""
                p1 = self.mem[self.pointer + 1]
                p2 = self.mem[self.pointer + 2]
                p3 = self.mem[self.pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                op1 = self.operand(p1, p1_mode)
                op2 = self.operand(p2, p2_mode)
                mem_pointer = self.mem_pointer(p3, p3_mode)

                result = int(op1 < op2)
                self.mem[mem_pointer] = result

                log.debug("OC%d Storing %d to mem[%d]", opcode, result, mem_pointer)

                self.pointer += 4
            elif opcode == 8:
                """Equals"""
                p1 = self.mem[self.pointer + 1]
                p2 = self.mem[self.pointer + 2]
                p3 = self.mem[self.pointer + 3]

                param_modes, p1_mode = divmod(param_modes, 10)
                p3_mode, p2_mode = divmod(param_modes, 10)

                op1 = self.operand(p1, p1_mode)
                op2 = self.operand(p2, p2_mode)
                mem_pointer = self.mem_pointer(p3, p3_mode)

                result = int(op1 == op2)
                self.mem[mem_pointer] = result
                log.debug("OC%d Storing %d to mem[%d]", opcode, result, mem_pointer)

                self.pointer += 4
            elif opcode == 9:
                """Adjust relative base"""
                log.debug("OC%d Current relative base %d", opcode, self.relative_base)
                p1 = self.mem[self.pointer + 1]
                op1 = self.operand(p1, param_modes)

                self.relative_base += op1
                log.debug("OC%d New relative base %d", opcode, self.relative_base)

                self.pointer += 2
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
