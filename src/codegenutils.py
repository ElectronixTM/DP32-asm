"""
В этом файле определяются функции, которые помогут в генерации кода
для процессора DP32. По большей части он покрывает только команды
процессору и не затрагивает диррективы резервирования памяти
"""

from abstracts import Register, Condition, Identifier, MemPtr, RawDataSizes
import optable
from command import Command, CommandSizes, MAX_FIELD_VAL
import math

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

def calc_raw_data_size(raw_data_size: int, data: list[int]) -> int:
    return math.ceil(len(data) * raw_data_size / 32) 

def handle_raw_data(size: RawDataSizes, data: list[int]) -> bytearray:
    """
    Записывает в память числа в Big Endian нотации, соблюдая выравнивание в 
    32 бита, для того, чтобы не сбивалось чтение
    """
    # Максимальная длина хекса для этого размера
    max_hex_size = (size // 8) * 2
    result = bytearray()
    for number in data:
        hex_repr = hex(number)[2:].rjust(max_hex_size, "0")
        if len(hex_repr) > max_hex_size:
            raise ValueError(f"Number {number} from param `data` exceeds "
                             "limits for the given size ({size} bits)")
        print(hex_repr)
        result += bytearray.fromhex(hex_repr)
    # До скольки надо добить нулями итоговый массив
    adjust = calc_raw_data_size(size, data) * 4
    return result.ljust(adjust, b'\x00')

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

