"""
Набор классов, которые используются почти во всех компонентах ассемблера
после завершения стадии синтаксического анализа
"""
from dataclasses import dataclass, field
from enum import IntFlag, IntEnum

@dataclass(frozen=True)
class Register:
    index: int

@dataclass(frozen=True)
class Label:
    name: str

@dataclass(frozen=True)
class Identifier:
    name: str

@dataclass(frozen=True)
class MemPtr:
    reg: Register
    disp: int | Identifier = 0
    # Плохая практика - на стадии ассемблера мне потребовалась
    # эта дополнительная информация, поэтому я ее захардкодил
    # сюда. Так делать плохо, но вряд ли я переделаю
    force_32: bool = False

class ConditionFlags(IntFlag):
    I = 1 << 3
    V = 1 << 2
    N = 1 << 1
    Z = 1 << 0

@dataclass(frozen=True)
class Condition:
    cond: ConditionFlags = ConditionFlags(0)

class RawDataSizes(IntEnum):
    BYTE = 8
    HALFWORD = 16
    WORD = 32

@dataclass
class RawData:
    size: RawDataSizes
    operands: list[int] = field(default_factory=list)

    def add_operand(self, operand: int):
        self.operands.append(operand)

@dataclass
class Operation:
    mnemonic: str
    operands: list[Register | int | Identifier | MemPtr] = field(default_factory=list)

    def add_operand(self, operand: Register | int) -> None:
        self.operands.append(operand)

