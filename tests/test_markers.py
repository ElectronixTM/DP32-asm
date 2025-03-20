"""
Данный пакет тестов проверяет, не летят ли у меня адреса операндов
при использовании маркеров в выражениях. Напоминаю, что маркер - 
всегда 32 битное число независимо от того, куда он указывает, хоть
на ноль, хоть на 
"""
import pytest
from src.abstracts import *
from src.main import assemble

# интересный факт, в этом ассемблере всем давно насрать на пробелы, так что
# свои тестовые примеры пишутся через пробел


@pytest.mark.parametrize("source,index,expected",
                         [
                             ("x: dw 0 load r1 [r255 + x] dw 0 0", 2*4, "00000000"),
                             ("dw 0 12 0 load r1 [r255 + x] dw 0 x: dw 0 0 0", 4*4, "00000006"),
                             ("dw" + " 0xff" * 12 + " load r1 [r255 + x] dw 0 x: dw 0 0 0", 13*4, "0000000f")
                         ]
                         )
def test_absolute_addr(source, index, expected):
    assembled = assemble(source)
    addr = assembled[index:index+4]
    print("HEX: ", assembled.hex())
    assert addr.hex() == expected

@pytest.mark.parametrize("source,index,expected",
                         [
                             ("dw" + " 0" * 12 + " store [r25 + rel x] r2 "
                              "dw" + " 0" * 4 + " x: dw 0xff 0xff",
                              13*4, "00000005"),
                             ("dw 0 0 y: dw 0xff 0xff load r2 [r1 + rel x] "
                              "dw 0 0 0 load r3 [r1 + rel y] dw 0 0 0 x: "
                              "dw 0 0", 10 * 4, "fffffff9"),
                             ("dw 0 0 y: dw 0xff 0xff load r2 [r1 + rel x] "
                              "dw 0 0 0 load r3 [r1 + rel y] dw 0 0 0 x: "
                              "dw 0 0", 5 * 4, "0000000a")
                         ]
                         )
def test_rel_addr(source, index, expected):
    assembled = assemble(source)
    addr = assembled[index:index+4]
    print("HEX: ", assembled.hex())
    assert addr.hex() == expected
