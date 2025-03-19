from dataclasses import dataclass, field
from abstracts import Operation, Identifier, Label, Register, MemPtr
import codegenutils
import optable
from command import Command, CommandSizes, MAX_FIELD_VAL
from collections import OrderedDict

@dataclass
class Assembler:
    """
    Класс, задачей которого становится разрешение имен, подстановка
    адресов и кодогенерация на фундаменте остальных написанных инструментов
    """
    
    # Global Addresses Table
    GAT: OrderedDict[Identifier, int] = field(default_factory=OrderedDict)

    def assemble(self, oplist: list[Operation | Label]) -> bytearray:
        """
        Выполняет двухпроходное ассемблирование того, что было подано на вход
        """
        self._construct_GAT(oplist)
        code = bytearray()
        for op in oplist:
            if isinstance(op, Label):
                continue
            else:
                command = self._assemble_operation(op)
                code += command.to_bytearray()
        return code

    def clear(self):
        """
        Purges the contents of GAT. Needed if you want to assemble multiple
        source texts with the same object
        """
        self.GAT = OrderedDict()

    def _resolve_identifier(self, id_: Identifier) -> int:
        return self.GAT[id_]

    def _resolve_identifiers(self, op: Operation) -> list[Register | int | MemPtr]:
        result: list[Register | int | MemPtr] = []
        for operand in op.operands:
            if isinstance(operand, Identifier):
                result.append(self._resolve_identifier(operand))
            elif isinstance(operand, MemPtr) and isinstance(operand.disp, Identifier):
                result.append(
                        MemPtr(
                            operand.reg,
                            self._resolve_identifier(operand.disp),
                            operand.force_32
                            )
                        )
            else:
                result.append(operand)
        return result

    def _codegen_mem_op(self, opcode, operands: list[Register | int | MemPtr]) -> Command:
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
                    if mem.force_32 or mem.disp > MAX_FIELD_VAL
                    else CommandSizes.DEFAULT)
            return codegenutils.handle_mem_op(
                    opcode,
                    r,
                    mem.reg,
                    mem.disp,
                    size
                    )
        raise ValueError("Unable to construct command with given parameters")
        

    def _assemble_operation(self, operation: Operation) -> Command:
        """
        Ассемблирует поданную на вход команду. Если в команде
        присутствуют идентификаторы, он пытается их разрешить
        """
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
            return codegenutils.handle_branch_op(opdesc.opcode, *operands)
        else:
            raise ValueError("Unknown layout encountered")

    def _get_op_desc(self, op: Operation) -> optable.OpcodeDescription:
        op_types = tuple(map(codegenutils.typedef_candidate, op.operands))
        opdesc = optable.get_opdesc(op.mnemonic, op_types)
        return opdesc

    # TODO: Вероятно в будущем потребуется логика, связанная с
    # резервированием памяти. Это поменяет реализацию этой функции
    def _get_op_size(self, op: Operation) -> int:
        """
        Получает размер инструкции, не выполняя ассемблирование. Необходим
        на первом проходе ассемблера, когда адреса необходимо вычислить не
        проводя ассемблирование целиком
        """
        opdesc= self._get_op_desc(op)
        return 2 if opdesc.expanded else 1

    def _construct_GAT(self, oplist: list[Operation | Label]) -> None:
        """
        Вызывается при первом проходе ассемблера по файлу - составляет
        таблицу переводов идентификаторов в адреса в памяти
        """
        cur_addr = 0
        for op in oplist:
            if isinstance(op, Label):
                self.GAT[Identifier(op.name)] = cur_addr
            else:
                cur_addr += self._get_op_size(op)

if __name__ == "__main__":
    from lexer import DPLexer
    from parser import DPParser
    a = Assembler()
    text = "add r2 r1 2"
    l = DPLexer()
    p = DPParser()
    ast = p.parse(l.tokenize(text))
    print(ast)
    assert isinstance(ast, list) and all(isinstance(x, (Operation, Label)) for x in ast)
    x = a.assemble(ast)
    print(x.hex())

