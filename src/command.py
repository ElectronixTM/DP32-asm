"""
Класс Command фактически занимается хранением бинарных полей,
которые почти всегда одни и те же у разных комманд. Может
иметь размер 32 или 64 бита. Позволяет относительно комфортно
заниматься сборкой очередной команды для ассемблера
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Any
from hexutils import tohex, unsigned_to_signed

class CommandSizes(IntEnum):
    DEFAULT = 32
    DOUBLED = 64

# restrictions
POSSIBLE_OPCODES = (list(range(0x0, 0x8))
                     +[0x10, 0x11, 0x12, 0x13, 0x20, 0x21, 0x30, 0x31, 0x40, 0x41, 0x50])
MIN_FIELD_VAL = -128
MAX_FIELD_VAL = 127

REG_COUNT = 256

def _set_field(attr: str):
    def set_field(self, value: int) -> None:
        if not self._check_reg_index_boundaries(value):
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
        lower_half = bytearray([
            self.opcode, self.r3_or_flags,
            self.r1, self.r2_or_const & ((1 << 8) - 1)
            ])
        upper_half = bytearray.fromhex(
                tohex(
                    self._extra,
                    maxbits=32
                    ).rjust(8, "0")
                )
        if self.size == CommandSizes.DEFAULT:
            return lower_half
        elif self.size == CommandSizes.DOUBLED:
            return lower_half + upper_half
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
    # r2_or_const = property(fget=_get_field("_r2_or_const"),
    #               fset=_set_field("_r2_or_const"))

    @property
    def r2_or_const(self) -> int:
        return self._r2_or_const

    @r2_or_const.setter
    def r2_or_const(self, value: int) -> None:
        print("value:", value)
        if MIN_FIELD_VAL <= value <= REG_COUNT:
            self._r2_or_const = value
            return
        raise ValueError("Passed value exceeds the limits for this "
                         "field. Make sure you use numbers from "
                         "-127 - 255 interval")

    @property
    def extra(self):
        return self._extra

    @extra.setter
    def extra(self, value: int):
        if len(tohex(value, CommandSizes.DEFAULT)) > 8:
            raise ValueError("Passed value exceeds limits. Make sure "
                             "your number in boundaries of 0 and "
                             "0xFFFFFFFF")
        self._extra = value

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: CommandSizes) -> None:
        if not value in CommandSizes:
            raise ValueError("Inappropriate size. Should be "
                             f"32 or 64, {value} passed")
        self._size = value
    
    def _check_reg_index_boundaries(self, value: int) -> bool:
        if not 0 <= value <= REG_COUNT:
            return False
        return True

if __name__ == "__main__":
    b = bytearray([1, 0xff])
    print(b)
