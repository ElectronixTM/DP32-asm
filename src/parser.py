from sly import Parser
from lexer import DSPLexer
from abstracts import *

class DSPParser(Parser):
    tokens = DSPLexer.tokens

    @_("operations_list operation")
    def operations_list(self, t):
        t.operations_list.append(t.operation)
        return t

    @_('operation ID')
    def operation(self, t):
        id_ = Identifier(t.ID)
        t.operation.add_operand(id_)
        return t.operation

    @_('operation NUMBER')
    def operation(self, t):
        t.operation.add_operand(t.NUMBER)
        return t.operation

    @_("operation REGISTER")
    def operation(self, t):
        r = Register(int(t.REGISTER[1:]))
        t.operation.add_operand(r)
        return t.operation

    @_('OPCODE')
    def operation(self, t):
        print(*t)
        return Operation(t.OPCODE)

    @_("operation")
    def operations_list(self, t):
        return [t.operation]

if __name__ == "__main__":
    l = DSPLexer()
    text = "add r1 r2 sub a b"
    p = DSPParser()
    print(p.parse(l.tokenize(text)))
