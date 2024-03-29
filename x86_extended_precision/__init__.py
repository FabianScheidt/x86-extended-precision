from __future__ import annotations

import logging
import struct
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


def deconstruct_extended_precision(
    input_bytes: bytes,
    byteorder: Literal["little", "big"] = "little",
) -> tuple[int, int, int]:
    if len(input_bytes) != 10:  # noqa: PLR2004
        raise Exception("Expected 10 bytes, got %d" % len(bytes))  # noqa: TRY002

    b = int.from_bytes(input_bytes, byteorder=byteorder)

    m = b & bitmask(EXTENDED_MANTISSA_LENGTH)
    b >>= EXTENDED_MANTISSA_LENGTH
    e = b & bitmask(EXTENDED_EXPONENT_LENGTH)
    b >>= EXTENDED_EXPONENT_LENGTH
    s = b

    return s, e, m


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
    if not (0 <= e_double < bitmask(DOUBLE_EXPONENT_LENGTH)):
        msg = f"Exponent { e } does not fit into 64 bit double"
        raise ValueError(msg)

    # Log a warning if we loose precision, as we have fewer bits for the mantissa
    if m & bitmask(MANTISSA_OFFSET) > 0:
        logger.warning("Loosing precision during conversion to double")

    # Assemble resulting double
    double = s_double
    double <<= DOUBLE_EXPONENT_LENGTH
    double |= e_double
    double <<= DOUBLE_MANTISSA_LENGTH
    double |= m_double

    return struct.unpack("<d", double.to_bytes(8, byteorder="little"))[0]
