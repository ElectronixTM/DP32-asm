"""
Набор классов, которые используются почти во всех компонентах ассемблера
после завершения стадии синтаксического анализа
"""
from dataclasses import dataclass, field
from enum import IntFlag

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
    reg: Register | None = None
    disp: int | Identifier = 0

class ConditionFlags(IntFlag):
    I = 1 << 3
    V = 1 << 2
    N = 1 << 1
    Z = 1 << 0

@dataclass(frozen=True)
class Condition:
    cond: ConditionFlags = ConditionFlags(0)

@dataclass
class Operation:
    mnemonic: str
    operands: list[Register | int | Identifier | MemPtr] = field(default_factory=list)

    def add_operand(self, operand: Register | int) -> None:
        self.operands.append(operand)

