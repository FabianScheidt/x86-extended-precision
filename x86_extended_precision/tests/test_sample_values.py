from x86_extended_precision import double_from_extended_precision_bytes


def test_sample_values() -> None:
    assert double_from_extended_precision_bytes(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") == 0.0
    assert double_from_extended_precision_bytes(b"\x00\x68\x66\x66\x66\x66\x66\x8a\x04\x40") == 34.6
    assert double_from_extended_precision_bytes(b"\x00\x68\x66\x66\x66\x66\x66\x86\x01\x40") == 4.2
    assert double_from_extended_precision_bytes(b"\x00\x00\x00\x00\x00\x00\x00\x8c\x04\x40") == 35.0
    assert double_from_extended_precision_bytes(b"\x00\x00\x00\x00\x00\x00\x00\xc0\x01\x40") == 6.0
    assert double_from_extended_precision_bytes(b"\x00\x00\x00\x00\x00\x00\x00\xc8\x03\x40") == 25.0
    assert double_from_extended_precision_bytes(b"\x00\x68\x66\x66\x66\x66\x66\xf6\x01\x40") == 7.7
    assert double_from_extended_precision_bytes(b"\x00\x30\x33\x33\x33\x33\x33\x89\x04\x40") == 34.3
    assert double_from_extended_precision_bytes(b"\x00\x00\x00\x00\x00\x00\x00\xc0\x01\x40") == 6.0
