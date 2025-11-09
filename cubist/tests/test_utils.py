"""Tests for cubist._utils functions"""

import pytest

from .._utils import _format
from .conftest import no_raise


@pytest.mark.parametrize(
    "val,raises,returns",
    [
        (1 + 1j, pytest.raises(ValueError), None),
        (1234567890123456413122, no_raise(), "1234567890123460000000"),
        (-1234567890123456413122, no_raise(), "-1234567890123460000000"),
        (1234567890123.4567, no_raise(), "1234567890123.46"),
        (-1234567890123.4567, no_raise(), "-1234567890123.46"),
        (123.45678901234567, no_raise(), "123.456789012346"),
        (-123.45678901234567, no_raise(), "-123.456789012346"),
        (123.456789, no_raise(), "123.456789"),
        (-123.456789, no_raise(), "-123.456789"),
        (None, no_raise(), None),
    ],
)
def test_format(val, raises, returns):
    """Test formatting numeric values"""
    with raises:
        assert _format(val) == returns
