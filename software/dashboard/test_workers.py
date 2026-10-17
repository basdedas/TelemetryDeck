import math
from workers import parse_line


def test_valid_line_returns_dict():
    assert parse_line(b"222,23.89,968.75,47.73,760,-3\r\n") == {
        "t": 0.222,
        "temp": 23.89,
        "pressure": 968.75,
        "humidity": 47.73,
        "pot": 760,
        "enc": -3,
    }


def test_comment_line_returns_none():
    assert parse_line(b"# rate set to 500\r\n") is None


def test_too_few_fields_returns_none():
    assert parse_line(b"222,23.89,968.75") is None


def test_too_many_fields_returns_none():
    assert parse_line(b"222,23.89,968.75,47.73,760,0,99") is None


def test_non_number_returns_none():
    assert parse_line(b"222,abc,968.75,47.73,760,0") is None


def test_empty_line_returns_none():
    assert parse_line(b"\r\n") is None


def test_nan_humidity_is_accepted():
    result = parse_line(b"222,23.89,968.75,nan,760,0")
    assert math.isnan(result["humidity"])