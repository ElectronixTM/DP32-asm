"""
Файл, в котором захардкожены все опкоды, и соответствующие им операнды.
В целом наверняка между опкодами есть какие-то очевидные закономерности,
которые позволяют не вбивать все возможности сюда, но к сожалению я их
не увидел. Может вы окажетесь наблюдательнее
"""
from dataclasses import dataclass
from enum import IntEnum, auto
from command import *
from abstracts import Register, Condition
from typing import TypeAlias

# тип данных, который для каждого отдельного типа
# опеации хранит различные варианты ее опкодов для
# разных типов аргументов

class OpcodeLayout(IntEnum):
    MATH = auto()
    MEMORY = auto()
    BRANCHING = auto()

@dataclass
class OpcodeDescription:
    opcode: int
    oplayout: OpcodeLayout
    expanded: bool = False

# несколько фиктивных типов для того, чтобы просто разделять разные опкоды
# зависящие только от размера операнда, так как в питоне размер явно не
# задается
# I8 = type("I8", (object,), {})
# I32 = type("I32", (object,), {})
class I8: pass
class I32: pass
# LongMem - mem address with 32 bit dispp
#LMem = type("LMem", (object,), {})
class LMem: pass
# ShortMem - mem address with 8 bit disp or without it
#SMem = type("LMem", (object,), {})
class SMem: pass


OpTable: TypeAlias = dict[tuple[type, ...], OpcodeDescription]

# Чтобы это дело не растягивалось на несколько километров, создам алиасы
Lout = OpcodeLayout
Desc = OpcodeDescription

OP_TABLE: dict[str, OpTable] = {
        "add": {
            (Register, Register, Register): Desc(0, Lout.MATH),
            (Register, Register, I8): Desc(10, Lout.MATH)
            },
        "sub": {
            (Register, Register, Register): Desc(1, Lout.MATH),
            (Register, Register, I8): Desc(11, Lout.MATH)
            },
        "mul": {
            (Register, Register, Register): Desc(2, Lout.MATH),
            (Register, Register, I8): Desc(12, Lout.MATH)
            },
        "div": {
            (Register, Register, Register): Desc(3, Lout.MATH),
            (Register, Register, I8): Desc(13, Lout.MATH)
            },
        "and": {
            (Register, Register, Register): Desc(4, Lout.MATH),
            },
        "or": {
            (Register, Register, Register): Desc(5, Lout.MATH),
            },
        "xor": {
            (Register, Register, Register): Desc(6, Lout.MATH),
            },
        "mask": {
            (Register, Register, Register): Desc(7, Lout.MATH),
            },
        "load": {
            (Register, LMem): Desc(20, Lout.MEMORY, expanded=True),
            (Register, SMem): Desc(30, Lout.MEMORY)
        },
        "store": {
            (Register, LMem): Desc(21, Lout.MEMORY, expanded=False),
            (Register, SMem): Desc(31, Lout.MEMORY)
            },
        "branch": {
            (Condition, I32): Desc(40, Lout.MEMORY),
            (Condition, I8): Desc(50, Lout.MEMORY),
            (Condition, LMem): Desc(41, Lout.MEMORY),
            # conditions are effectively integers, so it's 
            # also possible to just pass them directly
            (I8, I32): Desc(40, Lout.MEMORY),
            (I8, I8): Desc(50, Lout.MEMORY),
            (I8, LMem): Desc(41, Lout.MEMORY)
            #? (Condition, SMem): Desc(51, Lout.MEMORY) В описании
            # не указан, поэтому и у меня не будет
            }
        }

def get_opdesc(mnemonic: str, ops_types: tuple[type, ...]) -> OpcodeDescription:
    """
    Fetches appropriate operation description from `OP_TABLE`
    using given info on operands and mnemonic
    """
    candidates = OP_TABLE[mnemonic]
    return candidates[ops_types]
