"""
Набор классов, которые используются почти во всех компонентах ассемблера
после завершения стадии синтаксического анализа
"""
from dataclasses import dataclass, field
from enum import IntFlag, Flag, IntEnum, auto
import errorwatcher

@dataclass(frozen=True)
class Register:
    index: int

@dataclass(frozen=True)
class Label:
    name: str

class IdFlags(Flag):
    REL_ADDR = auto()

@dataclass(frozen=True)
class Identifier:
    name: str
    flags: IdFlags = field(
            default=IdFlags(0),
            compare=False,
            hash=False
            )

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

@errorwatcher.tracked
@dataclass
class RawData:
    size: RawDataSizes
    operands: list[int | Condition | Identifier] = field(default_factory=list)

    def add_operand(self, operand: int):
        self.operands.append(operand)

@errorwatcher.tracked
@dataclass
class Operation:
    mnemonic: str
    operands: list[Register | int |
                   Identifier | MemPtr |
                   Condition] = field(default_factory=list)

    def add_operand(
            self,
            operand: Register | int | Identifier | MemPtr | Condition
            ) -> None:
        self.operands.append(operand)


if __name__ == "__main__":
    print(type(Operation))
