import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype, is_datetime64_any_dtype


def _get_data_format(x: pd.Series):
    """

    :param x:
    :return:
    """
    if is_numeric_dtype(x):
        return "continuous."
    if is_string_dtype(x):
        return f"{','.join(set(x))}."
    # TODO: what does this do in R?
    if is_datetime64_any_dtype(x):
        return x


def quinlan_attributes(df: pd.DataFrame):
    """

    :param df:
    :return:
    """
    return {col_name: _get_data_format(col_data) for col_name, col_data in df.iteritems()}
