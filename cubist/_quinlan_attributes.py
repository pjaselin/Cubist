import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype, \
    is_datetime64_any_dtype, is_complex_dtype, is_float_dtype


def _get_data_format(x: pd.Series):
    """
    Function to obtain the data type/formatting information for a Pandas Series.
    Return "continuous." for continuous features, the set of values as a comma
    separated string for categorical features, and the column itself for 
    datetime features.

    Parameters
    ----------
    x : pd.Series
        Pandas Series from which to extract data type.
    
    Returns
    -------
    x : str
        String description of the Series data type.
    """
    # remove NAs from series
    x = x.dropna()
    # for numeric columns
    if is_numeric_dtype(x) or all([float == j for j in [type(i) for i in x.values]]):
        return "continuous."
    # for string columns
    elif is_string_dtype(x):
        x = x.astype(str)
        return f"{','.join(set(x))}."
    # for datetime columns
    elif is_datetime64_any_dtype(x):
        return x
    # otherwise the data is not supported here
    elif is_complex_dtype(x):
        raise ValueError("Complex data not supported")
    else:
        raise ValueError(f"Dtype {x.dtype} is not supported")


def quinlan_attributes(df: pd.DataFrame) -> dict:
    """
    Function to collect the data formatting information for each column in a Pandas DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Pandas DataFrame from which column data attributes are obtained.
    
    Returns
    -------
    x : dict
        Dictionary with keys as column names and values as the description of
        the data type.
    """
    return {col_name: _get_data_format(col_data) for col_name, col_data in df.iteritems()}
