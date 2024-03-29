import struct

from x86_extended_precision import (
    DOUBLE_EXPONENT_LENGTH,
    DOUBLE_MANTISSA_LENGTH,
    EXTENDED_EXPONENT_LENGTH,
    EXTENDED_MANTISSA_LENGTH,
    double_from_extended_precision_bytes,
)


def parse_bit_str(bit_str: str, e_len: int, m_len: int) -> bytes:
    split = [el for el in bit_str.split(" ") if el != ""]
    assert len(split) == 3, "Expected input to have three components: sign, exponent and fraction"
    assert len(split[0]) == 1, "Expected sign to have length 1"
    assert len(split[1]) == e_len, "Expected exponent to have length 11"
    assert len(split[2]) == m_len, "Expected fraction to have length 52"
    join = "".join(split)

    return bytes([int(join[i : i + 8], 2) for i in range(0, len(join), 8)])


def parse_double(bit_str: str) -> float:
    double_bytes = parse_bit_str(bit_str, DOUBLE_EXPONENT_LENGTH, DOUBLE_MANTISSA_LENGTH)
    return struct.unpack(">d", double_bytes)[0]


def parse_extended(bit_str: str) -> float:
    extended_bytes = parse_bit_str(bit_str, EXTENDED_EXPONENT_LENGTH, EXTENDED_MANTISSA_LENGTH)
    return double_from_extended_precision_bytes(extended_bytes, "big")
