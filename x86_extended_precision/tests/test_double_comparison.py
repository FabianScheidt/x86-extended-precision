import logging
import struct

from _pytest.logging import LogCaptureFixture

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


def test_one() -> None:
    d = "0     01111111111             0000000000000000000000000000000000000000000000000000"
    e = "0 011111111111111 1000000000000000000000000000000000000000000000000000000000000000"
    assert parse_double(d) == 1.0
    assert parse_extended(e) == 1.0


def test_two() -> None:
    d = "0     10000000000             0000000000000000000000000000000000000000000000000000"
    e = "0 100000000000000 1000000000000000000000000000000000000000000000000000000000000000"
    assert parse_double(d) == 2.0
    assert parse_extended(e) == 2.0


def test_negative_two() -> None:
    d = "1     10000000000             0000000000000000000000000000000000000000000000000000"
    e = "1 100000000000000 1000000000000000000000000000000000000000000000000000000000000000"
    assert parse_double(d) == -2.0
    assert parse_extended(e) == -2.0


def test_three() -> None:
    d = "0     10000000000             1000000000000000000000000000000000000000000000000000"
    e = "0 100000000000000 1100000000000000000000000000000000000000000000000000000000000000"
    assert parse_double(d) == 3.0
    assert parse_extended(e) == 3.0


def test_twentythree() -> None:
    d = "0     10000000011             0111000000000000000000000000000000000000000000000000"
    e = "0 100000000000011 1011100000000000000000000000000000000000000000000000000000000000"
    assert parse_double(d) == 23.0
    assert parse_extended(e) == 23.0


def test_min_subnormal_positive() -> None:
    d = "0     00000000000             0000000000000000000000000000000000000000000000000001"
    e = "0 011110000000000 1000000000000000000000000000000000000000000000000000100000000000"
    assert parse_extended(e) > 0
    assert parse_extended(e) == parse_double(d)


def test_max_subnormal() -> None:
    d = "0     00000000000             1111111111111111111111111111111111111111111111111111"
    e = "0 011110000000000 1111111111111111111111111111111111111111111111111111100000000000"
    assert parse_extended(e) > 0
    assert parse_extended(e) == parse_double(d)


def test_min_normal_positive() -> None:
    d = "0     00000000001             0000000000000000000000000000000000000000000000000000"
    e = "0 011110000000001 1000000000000000000000000000000000000000000000000000000000000000"
    assert parse_extended(e) > 0
    assert parse_extended(e) == parse_double(d)


def test_max() -> None:
    d = "0     11111111110             1111111111111111111111111111111111111111111111111111"
    e = "0 100001111111110 1111111111111111111111111111111111111111111111111111100000000000"
    assert parse_extended(e) > 0
    assert parse_extended(e) == parse_double(d)


def test_precision_warning(caplog: LogCaptureFixture) -> None:
    e1 = "0 100001111111110 1111111111111111111111111111111111111111111111111111100000000000"
    e2 = "0 100001111111110 1111111111111111111111111111111111111111111111111111110000000000"
    caplog.set_level(logging.WARNING)
    parse_extended(e1)
    assert caplog.text == ""
    parse_extended(e2)
    assert caplog.text != ""
