"""
Проверка ассемблирования условных переходов. Сильно интереснее тут конечно
прыжки по меткам, но если они работают отдельно, по идее должны работать и
тут. Другой вопрос уже что это штука сложнее и может у меня branch не 
работает вообще
"""

import pytest
from src.dp32assembler.abstracts import *
from src.dp32assembler.main import assemble

@pytest.mark.parametrize("source,index,expected",
                         [
                             ("dw 0 0 x: dw 0 0 branch {i=1vnz} rel x", 5*4, "fffffffc"),
                             ("dw 0 0 x: dw 0 0 branch {i=1vnz} -6", 4*4, "500f00fa")
                         ]
                         )
def test_rel_addr(source, index, expected):
    assembled = assemble(source)
    addr = assembled[index:index+4]
    print("HEX: ", assembled.hex())
    assert addr.hex() == expected
