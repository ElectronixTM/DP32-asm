"""
Фактически копия исходного ассемблера, но способного генерировать
отладочную информацию о программе и писать ее в файл dbg.json
"""

from dataclasses import dataclass, field
from assembler import Assembler, WORD_SIZE
from abstracts import Operation, Label, RawData
import errorwatcher
from typing import TypedDict

class DbgInstrDesc(TypedDict):
    """
    Описание отдельно взятой инструкции по определенному оффсету
    """
    length: int
    srcline: int

class DbgDict(TypedDict):
    """
    Урезанная версия полной отладочной информации, предоставляемой
    в файле dbg.json. Содержит ту информацию, которую может
    предоставить ассемблер
    """
    labels: dict[str, int]
    instructions: dict[int, DbgInstrDesc]

@dataclass
class DebugAssembler(Assembler):
    _dbg_dict: DbgDict = field(
            default_factory=lambda: DbgDict(
                labels={},
                instructions={},
                )
            )

    def assemble(self, oplist: list[Operation | Label | RawData]) -> bytearray:
        """
        Выполняет двухпроходное ассемблирование того, что было подано на вход
        """
        errors_list = errorwatcher.TrackedErrorsList(
                "errors occured while assembling instructions"
                )
        code = bytearray()
        try:
            self._construct_GAT(oplist)
        except errorwatcher.TrackedErrorsList as e:
            errors_list.exceptions.extend(e.exceptions)
        except errorwatcher.TrackedError as e:
            errors_list.exceptions.append(e)
        self._dump_GAT_to_dbg_dict()

        for op in oplist:
            try:
                instr_start_addr = len(code) // WORD_SIZE
                code += self._assemble_single_instr(op)
                if isinstance(op, Operation | RawData):
                    self._dump_instr_info(instr_start_addr, op)
                self._cur_addr = len(code) // WORD_SIZE
            except errorwatcher.TrackedError as e:
                errors_list.exceptions.append(e)

        if len(errors_list.exceptions) > 0:
            raise errors_list

        return code

    def _dump_GAT_to_dbg_dict(self) -> None:
        for identifier in self.GAT.keys():
            self._dbg_dict["labels"][identifier.name] = self.GAT[identifier]

    def _dump_instr_info(self, addr: int, op: Operation | RawData) -> None:
        if not hasattr(op, "_id"):
            return
        info = errorwatcher.ErrorWatcher().get_info_by_object(op)
        if not info:
            return
        line = info.lineno
        size = -1
        if isinstance(op, Operation):
            size = self._get_op_size(op)
        elif isinstance(op, RawData):
            size = self._get_raw_data_size(op)
        desc = DbgInstrDesc(length=size, srcline=line)
        self._dbg_dict["instructions"][addr] = desc

    def _get_dbg_dict(self) -> DbgDict:
        return self._dbg_dict

