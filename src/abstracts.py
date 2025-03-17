from dataclasses import dataclass, field

@dataclass(frozen=True)
class Register:
    index: int

@dataclass(frozen=True)
class Label:
    name: str

@dataclass(frozen=True)
class Identifier:
    name: str
    # ids: ClassVar[dict[str, int]]
    #
    # @classmethod
    # def get_id(cls, name: str) -> int:
    #     if name in cls.ids:
    #         return cls.ids[name]
    #     return max(cls.ids.values()) + 1 if len(cls.ids) > 0 else 0

    # def __init__(self, name: str):
    #     self.name = name
    #     if name in self.ids:
    #         self._id = self.ids[name]
    #     else:
    #         self.id_ = self.get_id(name)

@dataclass(frozen=True)
class MemPtr:
    reg: Register | None = None
    disp: int | Identifier | Label = 0

@dataclass
class Operation:
    mnemonic: str
    operands: list[Register | int | MemPtr] = field(default_factory=list)

    def add_operand(self, operand: Register | int) -> None:
        self.operands.append(operand)

