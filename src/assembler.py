from dataclasses import dataclass, field
from abstracts import (Operation, Identifier, Label, Condition,
                       Register, MemPtr, RawData, IdFlags)
import codegenutils
import optable
from command import Command, CommandSizes, MAX_FIELD_VAL
import enum
from hexutils import tohex
import errorwatcher

class AssembleFlags(enum.Flag):
    """
    Хранит информацию для ассемблера для отдельной команды.
    Должны сбрасываться после окончания ассемблирования отдельной команды
    """
    FORCE_EXPAND = enum.auto()

@dataclass
class Assembler:
    """
    Класс, задачей которого становится разрешение имен, подстановка
    адресов и кодогенерация на фундаменте остальных написанных инструментов
    """
    
    # Global Addresses Table
    GAT: dict[Identifier, int] = field(default_factory=dict)
    _flags: AssembleFlags = AssembleFlags(0)
    _cur_addr: int = 0
    # # Текущая ассемблируемая сущность. Нужна для отладки, чтобы прокидывать, от чего
    # # успел отъехать ассемблер. Далее это будет передано при формировании сообщения
    # # об ошибке
    # _cur_entity: Operation | RawData | None = None

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

        for op in oplist:
            try:
                if isinstance(op, Label):
                    continue
                elif isinstance(op, RawData):
                    code += codegenutils.handle_raw_data(op.size, op.operands)
                else:
                    command = self._assemble_operation(op)
                    code += command.to_bytearray()
                self._cur_addr = len(code) // 4
            except errorwatcher.TrackedError as e:
                errors_list.exceptions.append(e)

        if len(errors_list.exceptions) > 0:
            raise errors_list

        return code

    def clear(self):
        """
        Purges the contents of GAT. Needed if you want to assemble multiple
        source texts with the same object
        """
        self.GAT = {}
        self._flags = AssembleFlags(0)
        self._cur_addr = 0

    def _resolve_identifier(self, id_: Identifier) -> int:
        if not IdFlags.REL_ADDR in id_.flags:
            return self.GAT[id_]
        return self.GAT[id_] - self._cur_addr

    def _resolve_mem_ptr(self, mem_ptr: MemPtr) -> MemPtr:
        """
        Разрешает MemPtr, если есть необходимость, при
        этом проставляя флаги ассемблирования
        """
        if isinstance(mem_ptr.disp, Identifier):
            self._flags |= AssembleFlags.FORCE_EXPAND
            return MemPtr(
                    mem_ptr.reg,
                    self._resolve_identifier(mem_ptr.disp)
                    )
        # if mem_ptr.disp > MAX_FIELD_VAL:
        if len(tohex(mem_ptr.disp, CommandSizes.DEFAULT + 8)) > 2:
            self._flags |= AssembleFlags.FORCE_EXPAND
        return mem_ptr


    def _resolve_identifiers(
            self,
            op: Operation
            ) -> list[Register | int | MemPtr | Condition]:
        result: list[Register | int | MemPtr | Condition] = []
        for operand in op.operands:
            if isinstance(operand, Identifier):
                self._flags |= AssembleFlags.FORCE_EXPAND
                result.append(self._resolve_identifier(operand))
            elif isinstance(operand, MemPtr):
                result.append(self._resolve_mem_ptr(operand))
            else:
                result.append(operand)
        return result

    def _codegen_mem_op(
            self,
            opcode,
            operands: list[Register | int | MemPtr | Condition]
            ) -> Command:
        """
        Unpacks operands to fields of memory operation command. `MemPtr`
        objects should be in their resolved form, i.e no `Identifier`
        objects should present
        """
        r = None
        mem = None
        for op in operands:
            if isinstance(op, Register):
                r = op
            elif isinstance(op, MemPtr):
                mem = op
        if (isinstance(r, Register)
            and isinstance(mem, MemPtr)
            and isinstance(mem.disp, int)):
            size = (CommandSizes.DOUBLED
                    if AssembleFlags.FORCE_EXPAND in self._flags
                    else CommandSizes.DEFAULT)
            return codegenutils.handle_mem_op(
                    opcode,
                    r,
                    mem.reg,
                    mem.disp,
                    size
                    )
        raise ValueError("Unable to construct command with given parameters")

    def _codegen_branch_op(
            self,
            opcode,
            operands: list[Register | int | MemPtr | Condition]
            ) -> Command:
            size = (CommandSizes.DOUBLED
                    if AssembleFlags.FORCE_EXPAND in self._flags
                    else CommandSizes.DEFAULT)
            codegenutils.handle_branch_op
            ivnz = None
            reg = None
            disp = None
            for op in operands:
                if isinstance(op, Condition):
                    ivnz = op
                if isinstance(op, int):
                    disp = op
                if isinstance(op, MemPtr):
                    reg = op.reg
                    disp = op.disp
            if (isinstance(ivnz, Condition)
                and isinstance(disp, int)):
                return codegenutils.handle_branch_op(
                        opcode,
                        ivnz,
                        reg,
                        disp,
                        size
                        )
            raise ValueError("Unable to construct branch command with given parameters")

    def _assemble_operation(self, operation: Operation) -> Command:
        """
        Ассемблирует поданную на вход команду. Если в команде
        присутствуют идентификаторы, он пытается их разрешить
        """
        self._flags = AssembleFlags(0)
        opdesc = self._get_op_desc(operation)

        # Проверке типов происходящее тут не понравится
        # Но так как opdesc и так получается на основе типов, 
        # все на самом деле должно быть хорошо
        operands = self._resolve_identifiers(operation)
        if opdesc.oplayout == optable.OpcodeLayout.MATH:
            return codegenutils.handle_math_op(opdesc.opcode, *operands)
        elif opdesc.oplayout == optable.OpcodeLayout.MEMORY:
            return self._codegen_mem_op(opdesc.opcode, operands)
        elif opdesc.oplayout == optable.OpcodeLayout.BRANCHING:
            return self._codegen_branch_op(opdesc.opcode, operands)
        else:
            raise ValueError("Unknown layout encountered")

    def _get_op_desc(self, op: Operation) -> optable.OpcodeDescription:
        error = None
        op_types = tuple(map(codegenutils.typedef_candidate, op.operands))
        opdesc: optable.OpcodeDescription | None = None
        try:
            opdesc = optable.get_opdesc(op.mnemonic, op_types)
        except KeyError as e:
            error = errorwatcher.TrackedError(
                    op,
                    "Can't find valid opcode instruction"
                    f"'{op.mnemonic}' with given parameters",
                    e)
        if error: raise error
        assert isinstance(opdesc, optable.OpcodeDescription)
        return opdesc

    # TODO: Вероятно в будущем потребуется логика, связанная с
    # резервированием памяти. Это поменяет реализацию этой функции
    def _get_op_size(self, op: Operation) -> int:
        """
        Получает размер инструкции, не выполняя ассемблирование. Необходим
        на первом проходе ассемблера, когда адреса необходимо вычислить не
        проводя ассемблирование целиком
        """
        opdesc = self._get_op_desc(op)
        return 2 if opdesc.expanded else 1

    def _get_raw_data_size(self, raw_data: RawData):
        return codegenutils.calc_raw_data_size(
                raw_data.size,
                raw_data.operands
                )

    def _construct_GAT(self, oplist: list[Operation | Label | RawData]) -> None:
        """
        Вызывается при первом проходе ассемблера по файлу - составляет
        таблицу переводов идентификаторов в адреса в памяти
        """
        errors: list[errorwatcher.TrackedError] = []
        cur_addr = 0
        for op in oplist:
            try:
                if isinstance(op, Label):
                    self.GAT[Identifier(op.name)] = cur_addr
                elif isinstance(op, RawData):
                    cur_addr += self._get_raw_data_size(op)
                else:
                    cur_addr += self._get_op_size(op)
            except errorwatcher.TrackedError as e:
                print("TRACKED")
                errors.append(
                        errorwatcher.TrackedError(
                            e.failed_on,
                            msg="Couldn't determine size of operand "
                                'due to: "' + e.msg + '"',
                            prev_exception=e.prev_exception
                            )
                        )
            except Exception as e:
                print("UNTRACKED")
                error = errorwatcher.TrackedError(
                        op,
                        "Couldn't resolve size of given instruction",
                        e
                        )
                errors.append(error)
        if len(errors) != 0:
            raise errorwatcher.TrackedErrorsList(
                    "Errors occured while trying to determine operations sizes",
                    errors
                    )

if __name__ == "__main__":
    from lexer import DPLexer
    from parser import DPParser
    a = Assembler()
    text = "add r2 2"
    l = DPLexer()
    p = DPParser()
    ast = p.parse(l.tokenize(text))
    print(ast)
    assert isinstance(ast, list) and all(isinstance(x, (Operation, Label)) for x in ast)
    x = a.assemble(ast)
    print(x.hex())

