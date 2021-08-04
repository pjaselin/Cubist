import warnings

import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype
import numpy as np

from ._make_names_string import escapes


def validate_x(x):
    """Ensure input dataset is of a valid type and format"""
    if not isinstance(x, (pd.DataFrame, np.ndarray)):
        raise ValueError("X must be a Numpy Array or Pandas DataFrame")
    if isinstance(x, np.ndarray):
        if len(x.shape) != 2:
            raise ValueError("Input NumPy array has more than two dimensions, only a two dimensional matrices " \
                             "are allowed.")
        warnings.warn("Input data is a NumPy Array, setting column names to default `var0, var1,...`.")
        x = pd.DataFrame(x, columns=[f'var{i}' for i in range(x.shape[1])])
    return x


def r_format(x: float, digits: int = 15) -> str:
    """Python version of the R format function to return a number formatted as a 
    string rounded to `digits` number of digits from the left."""
    # if x is NA return NA
    if pd.isna(x):
        return x
    # get the count of whole number digits, i.e. the number of digits to the left of the decimal place
    whole_nums_count = len(str(int(x)))
    # Where there are decimal places that need to be rounded, round to digits - whole_nums_count decimal places
    if whole_nums_count < digits:
        remaining_decimals = digits - whole_nums_count
        return str(round(x, remaining_decimals))
    # Where there are no decimals that need to/can be rounded
    else:
        return str(x)


def make_data_string(x, y=None, w=None):
    """
    Converts input dataset array X into a string.

    Parameters
    ----------
    x : {pd.DataFrame} of shape (n_samples, n_features)
        The input samples.

    y : pd.Series
        The predicted values.
    
    w : ndarray of shape (n_samples,)
        Instance weights.

    Returns
    -------
    x : str
        Input dataset converted to a string and formatted per Cubist's requirements.
    """
    # copy Pandas objects so they aren't changed outside of this function
    x = x.copy(deep=True)
    y = y.copy(deep=True)

    # apply the escapes function to all string columns
    for col in x:
        if is_string_dtype(x[col]):
            x[col] = escapes(x[col].astype(str))

    # if y is None for model predictions, set y as a column of NaN values, which will become ?'s later
    if y is None:
        y = [np.nan] * x.shape[0]
        y = pd.Series(y)

    # format the y column for special charactesrs
    y = pd.Series(escapes(y.astype(str)))

    # insert the y column as the first column of x
    x.insert(0, "y", y)

    # handle weights matrix (?) TODO: validate
    if w is not None:
        column_names = list(x.columns) + [f"w{i}" for i in range(w.shape[1])]
        x = pd.concat([x, w], axis=1, ignore_index=True)
        x.columns = column_names

    # convert all columns to strings
    for col in x:
        if is_numeric_dtype(x[col]):
            x[col] = x[col].apply(r_format)
            x[col] = x[col].astype(str)
        else:
            x[col] = x[col].astype(str)

    # remove leading whitespace from all elements
    x = x.applymap(lambda a: a.lstrip())

    # replace missing values with ?
    x = x.fillna("?")
    x = x.replace("nan", "?")

    # convert dataframe to list of lists
    x = x.to_numpy().tolist()

    # merge each sublist into single strings with entries separated by commas
    x = [','.join(row) for row in x]

    # join all row strings into a single string separated by \n's
    x = "\n".join(x)
    return x
