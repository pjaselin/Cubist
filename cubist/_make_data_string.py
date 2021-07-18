import pandas as pd
import numpy as np
from ._make_names_string import escapes
from pandas.api.types import is_string_dtype, is_numeric_dtype


def _format(x, digits=15):
    if pd.isna(x):
        return x
    whole_nums_count = len(str(int(x)))
    # case where there are decimal places that need to be rounded
    if whole_nums_count < digits:
        remaining_decimals = digits - whole_nums_count
        return str(round(x, remaining_decimals))
    # case where there are no decimals that need to/can be rounded
    else:
        return str(x)


def make_data_string(x, y=None, w=None):
    # get a dictionary with keys as column names and values as whether the column is a string dtype
    convert = {col: is_string_dtype(x[col]) for col in x}

    if True in convert.values():
        for col, value in convert.items():
            if value:
                x[col] = escapes(x[col].astype(str))

    # if y is None for model predictions, set y as a column of NaN values, which will become ?'s later
    if y is None:
        y = [np.nan] * x.shape[0]
        y = pd.Series(y)
    
    # unclear if this needs to be implemented in Python:
    # if y.isnull().all():
    #     y = escapes()
    # if (is.null(y))
    #     y < - rep(NA_real_, nrow(x))

    # format the y column for special charactesrs
    y = pd.Series(escapes(y.astype(str)))

    # insert the y column as the first column of x
    x.insert(0, "y", y)
    
    # handle weights matrix (?)
    if w is not None:
        column_names = list(x.columns) + [f"w{i}" for i in range(w.shape[1])]
        x = pd.concat([x, w], axis=1, ignore_index=True)
        x.columns = column_names

    # convert all columns to strings
    for col in x:
        if is_numeric_dtype(x[col]):
            x[col] = x[col].apply(_format)
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
    # join each row as comma separated entries
    x = [','.join(row) for row in x]
    # join all rows separated by \n
    x = "\n".join(x)
    return x

