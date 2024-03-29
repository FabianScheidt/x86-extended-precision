import pytest

from x86_extended_precision.tests.utils import parse_extended


def test_non_normalized() -> None:
    # Both are 2.0, but e2 is non-normalized (mantissa < 1)
    e1 = "0 100000000000000 1000000000000000000000000000000000000000000000000000000000000000"
    e2 = "0 100000000000001 0100000000000000000000000000000000000000000000000000000000000000"
    assert parse_extended(e1) == 2.0
    with pytest.raises(NotImplementedError):
        parse_extended(e2)
