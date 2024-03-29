import logging

import pytest
from _pytest.logging import LogCaptureFixture

from x86_extended_precision.tests.utils import parse_extended


def test_small_exponent_error() -> None:
    e1 = "0 011110000000000 1000000000000000000000000000000000000000000000000000100000000000"
    e2 = "0 011101111111111 1000000000000000000000000000000000000000000000000000100000000000"
    parse_extended(e1)
    with pytest.raises(ValueError, match="too small to convert to float"):
        parse_extended(e2)


def test_large_exponent_error() -> None:
    e1 = "0 100001111111110 1000000000000000000000000000000000000000000000000000000000000000"
    e2 = "0 100001111111111 1000000000000000000000000000000000000000000000000000000000000000"
    parse_extended(e1)
    with pytest.raises(ValueError, match="too large to convert to float"):
        parse_extended(e2)


def test_precision_warning(caplog: LogCaptureFixture) -> None:
    e1 = "0 100001111111110 1111111111111111111111111111111111111111111111111111100000000000"
    e2 = "0 100001111111110 1111111111111111111111111111111111111111111111111111110000000000"
    caplog.set_level(logging.WARNING)
    parse_extended(e1)
    assert caplog.text == ""
    parse_extended(e2)
    assert caplog.text != ""
