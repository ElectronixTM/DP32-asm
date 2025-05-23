"""
Проассемблировать отдельные инструкции без контекста остальной программы
возможно только в том случае, если эти инструкции не содержат метки.
Тестирование программ, которые используют метки затруднено необходимостью
писать более длинные программы. Здесь проверяется корректность подстановки
отдельных частей команды в поля
"""
import pytest
from src.dp32assembler.abstracts import *
from src.dp32assembler.main import assemble

@pytest.mark.parametrize("instr,expected",
                         [
                             ("add r3 r1 3", "10030103"),
                             ("add r3 r1 -1", "100301ff"),
                             ("add r3 r1 r4", "00030104"),
                             ("sub r3 r1 3", "11030103"),
                             ("sub r3 r1 r4", "01030104"),
                             ("sub r1 r2 -6", "110102fa"),
                             ("mul r3 r1 3", "12030103"),
                             ("mul r3 r1 r4", "02030104"),
                             ("div r3 r1 3", "13030103"),
                             ("div r3 r1 r4", "03030104"),
                         ]
                         )
def test_math_instructions(instr, expected):
    assembled = assemble(instr)
    assert assembled.hex() == expected

@pytest.mark.parametrize("instr,expected",
                         [
                             ("and r255 r7 r34", "04ff0722"),
                             ("or r255 r7 r34", "05ff0722"),
                             ("xor r255 r7 r34", "06ff0722"),
                             ("mask r255 r7 r34", "07ff0722")
                         ]
                         )
def test_logic_instructions(instr, expected):
    assembled = assemble(instr)
    assert assembled.hex() == expected


@pytest.mark.parametrize("instr,expected",
                         [
                             ("load r33 [r4 + 7]", "30210407"),
                             ("load r33 [r4 + 1024]", "20210400" + "400".rjust(8, "0")),
                             ("store [r4 + 7] r33", "31210407"),
                             ("store [r4 + 1024] r33", "21210400" + "400".rjust(8, "0"))
                         ]
                         )
def test_unresolving_memory_instructions(instr, expected):
    """
    Имеется в виду операции чтения и записи в память, в которых
    не участвуют имена меток, то есть нет необходимости
    в разрешении имен и подстановках. А значит метки не надо
    прописывать в кодах, что удобно
    """
    assembled = assemble(instr)
    print(assembled.hex())
    assert assembled.hex() == expected
