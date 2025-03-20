from sly import Parser
from lexer import DPLexer
from abstracts import *

DATA_SIZES_TABLE: dict[str, RawDataSizes] = {
        "db": RawDataSizes.BYTE,
        "dh": RawDataSizes.HALFWORD,
        "dw": RawDataSizes.WORD
        }

class DPParser(Parser):
    tokens = DPLexer.tokens

    @_("operations_list operation")
    def operations_list(self, t):
        t.operations_list.append(t.operation)
        return t.operations_list

    @_("operations_list data")
    def operations_list(self, t):
        t.operations_list.append(t.data)
        return t.operations_list


    @_("operations_list LABEL")
    def operations_list(self, t):
        l = Label(t.LABEL)
        t.operations_list.append(l)
        return t.operations_list

    #@_('operation ID')
    #def operation(self, t):
    #    id_ = Identifier(t.ID)
    #    t.operation.add_operand(id_)
    #    return t.operation

    @_('data NUMBER')
    def data(self, t):
        t.data.add_operand(t.NUMBER)
        return t.data

    @_('operation effectively_number')
    def operation(self, t):
        t.operation.add_operand(t.effectively_number)
        return t.operation

    @_("operation REGISTER")
    def operation(self, t):
        r = Register(int(t.REGISTER[1:]))
        t.operation.add_operand(r)
        return t.operation

    @_("operation mem")
    def operation(self, t):
        t.operation.add_operand(t.mem)
        return t.operation

    # TODO: Я провтыкал в методичке, что при использовании обращения к памяти
    # через такую конструкцию регистр указывать обязательно. Потом перепеши
    # это нормально, чтобы регистр строять был обязан
    @_("LBRACKET REGISTER [ PLUS ] [ effectively_number ] RBRACKET")
    def mem(self, t):
        reg = Register(int(t.REGISTER[1:]))
        disp_tuple = t[3]
        if len(disp_tuple) > 1:
            raise ValueError("only one number can be "
                             "used to address memory")
        disp: int | Identifier = 0
        d = disp_tuple[0]
        force_32 = False
        if d:
            if isinstance(d, str):
                disp = Identifier(d)
                force_32 = True
            else:
                disp = d
        return MemPtr(reg, disp, force_32)

    @_("NUMBER")
    def effectively_number(self, t):
        return t.NUMBER

    @_("REL ID")
    def effectively_number(self, t):
        return Identifier(
                t.ID,
                IdFlags.REL_ADDR
                )

    @_("ID")
    def effectively_number(self, t):
        return Identifier(t.ID)

    @_("CONDITION")
    def effectively_number(self, t):
        print(t.CONDITION)
        print(Condition(t.CONDITION))
        return Condition(t.CONDITION)

    @_('OPCODE')
    def operation(self, t):
        return Operation(t.OPCODE)

    @_('LABEL')
    def operations_list(self, t):
        return [Label(t.LABEL)]

    @_("RAW_DATA")
    def data(self, t):
        return RawData(DATA_SIZES_TABLE[t.RAW_DATA])

    @_("data")
    def operations_list(self, t):
        return [t.data]

    @_("operation")
    def operations_list(self, t):
        return [t.operation]


if __name__ == "__main__":
    l = DPLexer()
    text = "x: db 12 12 33"
    p = DPParser()
    print(p.parse(l.tokenize(text)))

