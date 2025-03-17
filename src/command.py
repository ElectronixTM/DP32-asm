"""
Класс Command фактически занимается хранением бинарных полей,
которые почти всегда одни и те же у разных комманд. Может
иметь размер 32 или 64 бита. Позволяет относительно комфортно
заниматься сборкой очередной команды для ассемблера
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Any

class CommandSizes(IntEnum):
    DEFAULT = 32
    DOUBLED = 64

# restrictions
POSSIBLE_OPCODES = (list(range(0, 8))
                     +[10, 11, 12, 13, 20, 21, 30, 31, 40, 41, 50])
MIN_FIELD_VAL = 0
MAX_FIELD_VAL = 0xFF

def _set_field(attr: str):
    def set_field(self, value: int) -> None:
        if not self._check_field_boundaries(value):
            raise ValueError("Passed value exceeds limits. Make sure "
                             "your number in boundaries of 0 and 255")
        setattr(self, attr, value)
    return set_field

def _get_field(attr: str):
    def get_field(self) -> Any:
        return getattr(self, attr)
    return get_field

@dataclass
class Command:
    _opcode: int = 0
    _r3_or_flags: int = 0
    _r1: int = 0
    _r2_or_const: int = 0
    _extra: int = 0
    _size: CommandSizes = CommandSizes.DEFAULT

    def to_bytearray(self) -> bytearray:
        lower_half = (
                (self.opcode << 24)
                +(self.r3_or_flags << 16)
                +(self.r1 << 8)
                +(self.r2_or_const)
            )
        upper_half = self.extra
        if self.size == CommandSizes.DEFAULT:
            return bytearray([lower_half])
        elif self.size == CommandSizes.DOUBLED:
            return bytearray([lower_half, upper_half])
        else:
            raise ValueError("Wrong size specified")
            
    @property
    def opcode(self) -> int:
        return self._opcode

    @opcode.setter
    def opcode(self, value: int) -> None:
        if value not in POSSIBLE_OPCODES:
            raise ValueError("Not possible opcode passed")
        self._opcode = value

    r3_or_flags = property(fget=_get_field("_r3_or_flags"),
                           fset=_set_field("_r3_or_flags"))
    r1 = property(fget=_get_field("_r1"),
                  fset=_set_field("_r1"))
    r2_or_const = property(fget=_get_field("_r2_or_const"),
                  fset=_set_field("_r2_or_const"))
    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self, value: int):
        if not 0 <= value <= 0xFFFFFFFF:
            raise ValueError("Passed value exceeds limits. Make sure "
                             "your number in boundaries of 0 and "
                             "0xFFFFFFFF")
        self._extra = value

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> int:
        if not value in CommandSizes:
            raise ValueError("Inappropriate size. Should be "
                             f"32 or 64, {value} passed")
        return self.size
    
    def _check_field_boundaries(self, value: int) -> bool:
        if not MIN_FIELD_VAL <= value <= MAX_FIELD_VAL:
            return False
        return True

if __name__ == "__main__":
    b = bytearray([1, 0xff])
    print(b)
