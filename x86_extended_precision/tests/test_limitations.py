import pytest

from x86_extended_precision.tests.utils import parse_extended


def test_unnormal() -> None:
    # Both are 2.0, but e2 is unnormal / non-normalized, as mantissa is less than 1
    e1 = "0 100000000000000 1000000000000000000000000000000000000000000000000000000000000000"
    e2 = "0 100000000000001 0100000000000000000000000000000000000000000000000000000000000000"
    assert parse_extended(e1) == 2.0
    with pytest.raises(NotImplementedError):
        parse_extended(e2)
