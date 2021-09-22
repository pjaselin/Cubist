import random
from contextlib import contextmanager

import pandas as pd
import numpy as np
import pytest

from cubist._quinlan_attributes import quinlan_attributes, _get_data_format, \
    _is_all_float_dtype, _is_all_int_dtype


int_series = pd.Series(random.sample(range(10, 30), 5))
float_series = pd.Series(np.random.uniform(low=0.5, high=13.3, size=(5,)))
str_series = pd.Series(["test0", "test1", "test2", "test3", "test4"])
complex_series = pd.Series([complex(0, i) for i in range(5)])
date_series = pd.Series(pd.date_range("2018-01-01", periods=5, freq="H"))
good_df = pd.DataFrame({"a": int_series,
                        "b": float_series,
                        "c": str_series,
                        "d": date_series})
bad_df = pd.DataFrame({"a": int_series,
                       "b": float_series,
                       "c": str_series,
                       "d": complex_series})


@contextmanager
def no_raise():
    yield


@pytest.mark.parametrize("test_input,expected", 
                        [(int_series, True), 
                         (float_series, False), 
                         (str_series, False),
                         (complex_series, False),
                         (date_series, False)])
def test_is_all_int_dtype(test_input, expected):
    assert _is_all_int_dtype(test_input) == expected



@pytest.mark.parametrize("test_input,expected", 
                        [(int_series, False), 
                         (float_series, True), 
                         (str_series, False),
                         (complex_series, False),
                         (date_series, False)])
def test_is_all_float_dtype(test_input, expected):
    assert _is_all_float_dtype(test_input) == expected


@pytest.mark.parametrize("test_input,expected,raises", 
                        [(int_series, "continuous.", no_raise()), 
                         (float_series, "continuous.", no_raise()), 
                         (str_series, f"{','.join(set(str_series.values))}.", no_raise()),
                         (complex_series, None, pytest.raises(ValueError)),
                         (date_series, date_series, no_raise())])
def test_get_data_format(test_input, expected, raises):
    with raises:
        try:
            assert any(_get_data_format(test_input) == expected)
        except TypeError:
            assert _get_data_format(test_input) == expected
        except Exception as exc:
            raise(exc)


@pytest.mark.parametrize("test_input,expected,raises", 
                        [(good_df, dict, no_raise()), 
                         (bad_df, dict, pytest.raises(ValueError))])
def test_quinlan_attributes(test_input, expected, raises):
    with raises:
        assert type(quinlan_attributes(test_input)) == expected
