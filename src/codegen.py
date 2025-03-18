"""
В этом файле определяются функции, которые помогут в генерации кода
для процессора DP32. По большей части он покрывает только команды
процессору и не затрагивает диррективы резервирования памяти
"""

from abstracts import Register, Condition, Operation, Identifier, MemPtr
import optable
from command import Command, CommandSizes, MAX_FIELD_VAL

def handle_math_opcode(
        opcode: int,
        r3: Register,
        r1: Register,
        r2_i8: Register | int
        ) -> Command:
    result = Command()
    result.opcode = opcode
    result.r3_or_flags = r3.index
    result.r1 = r1.index
    if isinstance(r2_i8, int):
        result.r2_or_const = r2_i8
    else:
        result.r2_or_const = r2_i8.index
    return result

def handle_mem_op(
        opcode: int,
        r3: Register,
        r1: Register,
        disp: int
        ) -> Command:
    result = Command()
    result.opcode = opcode
    result.r3_or_flags = r3.index
    result.r1 = r1.index
    if disp > MAX_FIELD_VAL:
        result.size = CommandSizes.DOUBLED
        result.extra = disp
    else:
        result.r2_or_const = disp
    return result

def handle_branch_op(
        opcode: int,
        ivnz: Condition,
        r1: Register | None,
        disp: int
        ) -> Command:
    result = Command()
    result.opcode = opcode
    result.r3_or_flags = ivnz.cond
    if r1:
        result.r1 = r1.index
    if disp > MAX_FIELD_VAL:
        result.size = CommandSizes.DOUBLED
        result.extra = disp
    return result

def _convert_candidates(
        operand: Register | int | Condition | Identifier | MemPtr
        ) -> type:
    if isinstance(operand, MemPtr):
        # TODO: решить эту проблему
        pass
    if not isinstance(operand, int):
        return type(operand)
    if operand > MAX_FIELD_VAL:
        return optable.I32
    else:
        return optable.I8

def assemble_operation(operation: Operation):
    candidates = optable.OP_TABLE[operation.mnemonic]
    operands = tuple(map(_convert_candidates, operation.operands))
    print(operands)
    winner = None
    for candidate in candidates.keys():
        if candidate == operands:
            winner = candidates[candidate]
            break
    print(winner)


if __name__ == "__main__":
    o = Operation(
            "add",
            [Register(12), 7]
            )
    assemble_operation(o)
