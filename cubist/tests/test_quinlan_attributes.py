"""Tests for obtaining Quinlan's attributes from input datasets"""

import random

import numpy as np
import pandas as pd
import pytest

from .._quinlan_attributes import (
    _get_data_format,
    _is_all_float_dtype,
    _is_all_int_dtype,
    _quinlan_attributes,
)
from .conftest import no_raise

# create sample series for different data types
int_series = pd.Series(random.sample(range(10, 30), 5))
float_series = pd.Series(np.random.uniform(low=0.5, high=13.3, size=(5,)))
str_series = pd.Series(["test0", "test1", "test2", "test3", "test4"])
complex_series = pd.Series([complex(0, i) for i in range(5)])
date_series = pd.Series(pd.date_range("2018-01-01", periods=5, freq="h"))
unsupported_series = pd.Series(["test0", "test1", "test2", "test3", np])
good_df = pd.DataFrame(
    {"a": int_series, "b": float_series, "c": str_series, "d": date_series}
)
bad_df = pd.DataFrame(
    {"a": int_series, "b": float_series, "c": str_series, "d": complex_series}
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (int_series, True),
        (float_series, False),
        (str_series, False),
        (complex_series, False),
        (date_series, False),
    ],
)
def test_is_all_int_dtype(test_input, expected):
    """Test integer data type"""
    assert _is_all_int_dtype(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (int_series, False),
        (float_series, True),
        (str_series, False),
        (complex_series, False),
        (date_series, False),
    ],
)
def test_is_all_float_dtype(test_input, expected):
    """Test float data type"""
    assert _is_all_float_dtype(test_input) == expected


@pytest.mark.parametrize(
    "test_input,expected,raises",
    [
        (int_series, "continuous.", no_raise()),
        (float_series, "continuous.", no_raise()),
        (str_series, f"{','.join(set(str_series.values))}.", no_raise()),
        (complex_series, None, pytest.raises(ValueError)),
        (date_series, date_series, no_raise()),
        (unsupported_series, None, pytest.raises(ValueError)),
    ],
)
def test_get_data_format(test_input, expected, raises):
    """Test classifying data types"""
    with raises:
        try:
            assert any(_get_data_format(test_input) == expected)
        except TypeError:
            assert _get_data_format(test_input) == expected
        except Exception as exc:
            raise exc


@pytest.mark.parametrize(
    "test_input,expected,raises",
    [(good_df, dict, no_raise()), (bad_df, dict, pytest.raises(ValueError))],
)
def test_quinlan_attributes(test_input, expected, raises):
    """Test obtaining quinlan attributes"""
    with raises:
        assert isinstance(_quinlan_attributes(test_input), expected)
