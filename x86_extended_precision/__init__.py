from __future__ import annotations

import logging
import struct
from math import ceil
from typing import Literal

logger = logging.getLogger(__name__)

DOUBLE_EXPONENT_LENGTH = 11
DOUBLE_EXPONENT_BIAS = 1023
DOUBLE_MANTISSA_LENGTH = 52

EXTENDED_EXPONENT_LENGTH = 15
EXTENDED_EXPONENT_BIAS = 16383
EXTENDED_MANTISSA_LENGTH = 64

BIAS_OFFSET = EXTENDED_EXPONENT_BIAS - DOUBLE_EXPONENT_BIAS
MANTISSA_OFFSET = EXTENDED_MANTISSA_LENGTH - DOUBLE_MANTISSA_LENGTH - 1


def bitmask(length: int) -> int:
    return (1 << length) - 1


def get_byte_count(exponent_length: int, mantissa_length: int) -> int:
    return ceil((1 + exponent_length + mantissa_length) / 8)


def deconstruct_floating_point(
    input_bytes: bytes,
    *,
    exponent_length: int,
    mantissa_length: int,
    byteorder: Literal["little", "big"] = "little",
) -> tuple[int, int, int]:
    byte_count = get_byte_count(exponent_length, mantissa_length)
    if len(input_bytes) != byte_count:
        msg = f"Expected { byte_count } bytes, got f{ len(input_bytes) }"
        raise ValueError(msg)

    b = int.from_bytes(input_bytes, byteorder=byteorder)

    m = b & bitmask(mantissa_length)
    b >>= mantissa_length
    e = b & bitmask(exponent_length)
    b >>= exponent_length
    s = b

    return s, e, m


def construct_floating_point(
    s: int,
    e: int,
    m: int,
    *,
    exponent_length: int,
    mantissa_length: int,
    byteorder: Literal["little", "big"] = "little",
) -> bytes:
    res = s
    res <<= exponent_length
    res |= e
    res <<= mantissa_length
    res |= m
    byte_count = get_byte_count(exponent_length, mantissa_length)
    return res.to_bytes(byte_count, byteorder=byteorder)


def deconstruct_extended_precision(
    input_bytes: bytes,
    byteorder: Literal["little", "big"] = "little",
) -> tuple[int, int, int]:
    return deconstruct_floating_point(
        input_bytes,
        exponent_length=EXTENDED_EXPONENT_LENGTH,
        mantissa_length=EXTENDED_MANTISSA_LENGTH,
        byteorder=byteorder,
    )


def double_from_extended_precision_bytes(
    input_bytes: bytes,
    byteorder: Literal["little", "big"] = "little",
) -> float:
    s, e, m = deconstruct_extended_precision(input_bytes, byteorder)

    # TODO: Handle special cases
    # https://en.wikipedia.org/wiki/Extended_precision#:~:text=x86%20Extended%20Precision%20value

    # Ensure that normalized form is used and drop the bit, as it is implicit/hidden for double-precision formats
    if (m >> (EXTENDED_MANTISSA_LENGTH - 1)) != 0x01:
        msg = "Non-normalized values are not supported"
        raise NotImplementedError(msg)
    m = m & bitmask(EXTENDED_MANTISSA_LENGTH - 1)

    # Convert components to double
    s_double = s
    e_double = e - BIAS_OFFSET
    m_double = m >> MANTISSA_OFFSET

    # Ensure that exponent fits into a 64 bit double (signed zero is implicit; no accidental conversion to infinity/NaN)
    if e_double < 0:
        msg = f"Exponent { e } too small to convert to float"
        raise ValueError(msg)
    if e_double >= bitmask(DOUBLE_EXPONENT_LENGTH):
        msg = f"Exponent { e } too large to convert to float"
        raise ValueError(msg)

    # Log a warning if we loose precision, as we have fewer bits for the mantissa
    if m & bitmask(MANTISSA_OFFSET) > 0:
        logger.warning("Loosing precision during conversion to double")

    # Assemble resulting double
    double_bytes = construct_floating_point(
        s_double,
        e_double,
        m_double,
        exponent_length=DOUBLE_EXPONENT_LENGTH,
        mantissa_length=DOUBLE_MANTISSA_LENGTH,
        byteorder="little",
    )
    return struct.unpack("<d", double_bytes)[0]
