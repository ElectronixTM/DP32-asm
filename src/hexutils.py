def tohex(num: int, maxbits: int) -> str:
    """
    Считает hex от положительных и отрицательных чисел
    """
    return hex(num & ((1 << maxbits) - 1))[2:]

def unsigned_to_signed(value: int, bits: int):
    """
    Переводит беззнаковое число в знаковое на основе переданной битности
    """
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value

def fromhex(hexstr: str, bits: int) -> int:
    """
    Разбирает число как знаковое, учитывая ожидаемую битность.
    """
    value = int(hexstr, 16)
    return unsigned_to_signed(value, bits)
