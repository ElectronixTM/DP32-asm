import pytest
from src.dp32assembler.abstracts import *
from src.dp32assembler.main import assemble

@pytest.mark.parametrize("source,expected",
                         [
                             ("db 1 2 3 4", "01020304"),
                             ("db 255 0x37 00 0x22", "ff370022"),
                             ("db 0x77", "77000000"),
                             ("db 0x77 0x22", "77220000"),
                             ("db 0x77 0x22 0x33", "77223300"),
                             ("db 0x77 0x22 0x33 0x00 0x44", "7722330044000000"),
                             # Стресс тест
                             ("db 0x77 0x22 0x33 0x00 "
                              "0x44 0 0 0x1 "
                              "0x1 0x1 0x1 00 "
                              "127",
                              "77223300"
                              "44000001"
                              "01010100"
                              "7f000000"),
                             ("db ", "")
                         ]
                         )
def test_db(source, expected):
    assembled = assemble(source)
    assert assembled.hex() == expected

@pytest.mark.parametrize("source,expected",
                         [
                             ("dh 0x1234 0x1234", "12341234"),
                             ("dh 0 0 1 2", "0000000000010002"),
                             ("dh 0 1 2", "0000000100020000"),
                             ("dh 0 1 2 3 4", "000000010002000300040000"),
                             ("dh ", "")
                         ]
                         )
def test_dh(source, expected):
    assembled = assemble(source)
    assert assembled.hex() == expected

@pytest.mark.parametrize("source,expected",
                         [
                             ("dw 0x2222", "00002222"),
                             ("dw 0x12345678", "12345678"),
                             ("dw 0x12345678 1", "1234567800000001"),
                             ("dw ", "")
                         ]
                         )
def test_dw(source, expected):
    assembled = assemble(source)
    assert assembled.hex() == expected
