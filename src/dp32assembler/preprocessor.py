"""
Препроцессор преобразует один набор токенов в другой набор токенов. Однако
это для умных людей, а мой препроцессор вычленяет все диррективы себе из
кода, составляет на их основе специальную таблицу замен и заменяет все
попадающиеся идентификаторы на них. Я не добавляю ничего умного, фактически
это просто re.sub)
"""
from dataclasses import dataclass
from .lexer import DPLexer
from sly.lex import Token
from typing import Iterator, Callable


@dataclass
class DPPreprocessor:
    """
    Парсит набор токенов, и превращает их в другой (если
    используются директивы препроцессору) или такой же 
    набор токенов
    """

    _directives: dict[str, Callable[[Iterator[Token]], list[Token]]]
    _preprocessing_table: dict[str | int, int | str]
    _resulting_tokens: list[Token]

    def __init__(self):
        self._preprocessing_table = {}
        self._resulting_tokens = []
        self._directives = {
                "define": self._process_define,
                "undefine": self._process_undef
                }

    def preprocess(self, tokens: Iterator[Token]) -> Iterator[Token]:
        """
        Превращает один набор токенов в другой набор токенов. 
        На практике можно было бы обойтись каким-нибудь re.sub
        (что фактичеси и будет сделано), но для расширяемости
        это оформляется в класс
        """
        for token in tokens:
            if token.type != "PREPROC_DIRECTIVE":
                self._resulting_tokens.append(
                        self._preprocess_token(token)
                        )
                continue
            try:
                self._resulting_tokens.extend(
                        self._directives[token.value](tokens)
                        )
            except StopIteration:
                raise SyntaxError(
                        f"Preprocessing directive \"{token.value}\" couldn't "
                        "obtain enough arguments"
                        )
        return iter(self._resulting_tokens)

    def _preprocess_token(self, token: Token) -> Token:
        """
        Если потребуется более сложный препроцессор, функция будет
        сильно усложнена, но так как на данный момент пользователю
        доступны лишь #define и #undefine, сойдет и так
        """
        if token.type != "ID":
            return token
        if token.value not in self._preprocessing_table:
            return token
        substitution = self._preprocessing_table[token.value]
        if isinstance(substitution, int):
            token.type = "NUMBER"
            token.value = substitution
        return token

    def _invoke_directive_handler(
            self,
            directive: Token,
            tokens: Iterator[Token]
            ) -> list[Token]:
        return self._directives[directive.value](tokens)

    def _process_define(self, tokens: Iterator[Token]) -> list[Token]:
        """
        Простейшая вариация дифайна, которая может позволить делать
        довольно мало всего и всегда требует 2 аргумента - что заменяем
        и на что заменяем
        """
        operands = tuple(next(tokens).value for _ in range(2))
        self._preprocessing_table[operands[0]] = operands[1]
        return []

    def _process_undef(self, tokens: Iterator[Token]) -> list[Token]:
        entry = next(tokens).value
        del self._preprocessing_table[entry]
        return []


if __name__ == "__main__":
    l = DPLexer()
    text = "#define x hello x: 0x20 add r1 r2 x"
    tokens = l.tokenize(text)
    # print(*tokens)
    prep = DPPreprocessor()
    print(*prep.preprocess(tokens))
    print(prep._preprocessing_table)
