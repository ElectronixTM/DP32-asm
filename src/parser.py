from sly import Parser
from lexer import DSPLexer
from abstracts import *

class DSPParser(Parser):
    tokens = DSPLexer.tokens

    @_("operations_list operation")
    def operations_list(self, t):
        t.operations_list.append(t.operation)
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

    @_("LBRACKET [ REGISTER ]  [ PLUS ] [ effectively_number ] RBRACKET")
    def mem(self, t):
        regs_tuple = t[1]
        if len(regs_tuple) > 1:
            raise ValueError("only one register can be "
                             "used to address memory")
        reg = regs_tuple[0]
        disp_tuple = t[3]
        if len(disp_tuple) > 1:
            raise ValueError("only one number can be "
                             "used to address memory")
        disp: int = disp_tuple[0] if disp_tuple[0] else 0
        return MemPtr(reg, disp)

    @_("NUMBER")
    def effectively_number(self, t):
        return t.NUMBER

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

    @_("operation")
    def operations_list(self, t):
        return [t.operation]

if __name__ == "__main__":
    l = DSPLexer()
    text = "branch {i=1vZ} [r11 + 5]"
    p = DSPParser()
    print(p.parse(l.tokenize(text)))

