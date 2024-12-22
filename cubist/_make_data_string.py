"""functions to create the Cubist datav_ input"""

import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype
import numpy as np

from ._make_names_string import _escapes
from ._utils import _format


def _make_data_string(x, y=None, w=None):
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
        Input dataset converted to a string and formatted per Cubist's
        requirements.
    """
    # apply the escapes function to all string columns
    for col in x:
        if is_string_dtype(x[col]):
            x[col] = _escapes(x[col].astype(str))

    # if y is None for model predictions, set y as a column of NaN values,
    # # which will become ?'s later
    if y is None:
        y = [np.nan] * x.shape[0]
        y = pd.Series(y)
    else:
        y = y.copy(deep=True)

    # format the y column for special charactesrs
    y = pd.Series(_escapes(y.astype(str)))

    # insert the y column as the first column of x
    x.insert(0, "y", y)

    # handle weights matrix (?) TODO: validate
    if w is not None:
        # [f"w{i}" for i in range(x.shape[1])]
        column_names = list(x.columns) + ["w"]
        x = x.assign(w=w)
        x.columns = column_names

    # convert all columns to strings
    for col in x:
        if is_numeric_dtype(x[col]):
            x[col] = x[col].apply(_format)
            x[col] = x[col].astype(str)
        else:
            x[col] = x[col].astype(str)

    # remove leading whitespace from all elements
    # handling pandas 2.2.2 feature change (applymap -> map)
    if hasattr(x, "map"):  # pragma: no cover
        x = x.map(lambda a: a.lstrip())
    else:  # pragma: no cover
        x = x.applymap(lambda a: a.lstrip())

    # replace missing values with ?
    x = x.fillna("?")
    x = x.replace("nan", "?")

    # convert dataframe to list of lists
    x = x.to_numpy().tolist()

    # merge each sublist into single strings with entries separated by commas
    x = [",".join(row) for row in x]

    # join all row strings into a single string separated by \n's
    x = "\n".join(x)
    return x
