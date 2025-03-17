from sly import Lexer

class DSPLexer(Lexer):
    tokens = {
            ID, OPCODE, REGISTER,
            LABEL, NUMBER,
            LBRACKET, RBRACKET
            }
    ignore = ' \t\n'
    ignore_comment = r';.*'

    # NEWLINE = r'\n+|;+'
    @_(r'r\d+')
    def REGISTER(self, t):
        if not 1 <= int(t.value[1:]) <= 256:
            raise ValueError("Пожалуйста, исопльзуйте регистры из набора r1-r256")
        return t
    LABEL = r'[_a-zA-Z]\w*:'
    ID = r'[_a-zA-Z]\w*'

    ID['add'] = OPCODE
    ID['sub'] = OPCODE
    ID['mul'] = OPCODE
    ID['div'] = OPCODE
    ID['and'] = OPCODE
    ID['or'] = OPCODE
    ID['xor'] = OPCODE
    ID['mask'] = OPCODE
    ID['load'] = OPCODE
    ID['store'] = OPCODE
    ID['branch'] = OPCODE

    @_(r"0x[0-9a-f]+",
       r"\d+")
    def NUMBER(self, t):
        if t.value.startswith("0x"):
            t.value = int(t.value, 16)
        else:
            t.value = int(t.value)
        return t


if __name__ == "__main__":
    l = DSPLexer()
    prog = "add r1 0x12"
    print(*l.tokenize(prog))
