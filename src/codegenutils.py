"""
В этом файле определяются функции, которые помогут в генерации кода
для процессора DP32. По большей части он покрывает только команды
процессору и не затрагивает диррективы резервирования памяти
"""

from abstracts import Register, Condition, Identifier, MemPtr
import optable
from command import Command, CommandSizes, MAX_FIELD_VAL

def handle_math_op(
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
        disp: int,
        size: CommandSizes = CommandSizes.DEFAULT
        ) -> Command:
    result = Command()
    result.opcode = opcode
    result.r3_or_flags = r3.index
    result.r1 = r1.index
    result.size = size
    if size == CommandSizes.DOUBLED:
        result.extra = disp
    else:
        result.r2_or_const = disp
    return result

def handle_branch_op(
        opcode: int,
        ivnz: Condition,
        r1: Register | None,
        disp: int,
        size: CommandSizes = CommandSizes.DEFAULT
        ) -> Command:
    result = Command()
    result.opcode = opcode
    result.r3_or_flags = ivnz.cond
    result.size = size
    if r1:
        result.r1 = r1.index
    if size == CommandSizes.DOUBLED:
        result.extra = disp
    return result

def typedef_candidate(
        operand: Register | int | Condition | MemPtr | Identifier
        ) -> type:
    """
    Принимает все операнды класса Operation и преобразует их в типы
    в соответствии с которыми они будут закодированы при ассемблировании
    """
    if isinstance(operand, Identifier):
        return optable.I32
    if isinstance(operand, MemPtr):
        if isinstance(operand.disp, Identifier):
            return optable.LMem
        elif operand.disp > MAX_FIELD_VAL:
            return optable.LMem
        else:
            return optable.SMem

    if not isinstance(operand, int):
        return type(operand)
    if operand > MAX_FIELD_VAL:
        return optable.I32
    else:
        return optable.I8

