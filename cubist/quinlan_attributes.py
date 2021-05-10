import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype, is_datetime64_any_dtype


def _get_data_format(x: pd.Series):
    """Function to obtain the data formatting information for a Pandas Series

    :param x: Input Pandas Series
    :return: Formatting information about the Series
    """
    # for numeric columns
    if is_numeric_dtype(x):
        return "continuous."
    # for string columns
    if is_string_dtype(x):
        return f"{','.join(set(x))}."
    # for datetime columns
    if is_datetime64_any_dtype(x):
        return x
    # otherwise the data is not supported here
    else:
        raise NotImplementedError


def quinlan_attributes(df: pd.DataFrame) -> dict:
    """Function to collect the data formatting information for each column in a Pandas DataFrame

    :param df: Input Pandas DataFrame
    :return: Dictionary with column names as keys and data format information as values
    """
    return {col_name: _get_data_format(col_data) for col_name, col_data in df.iteritems()}
