import pandas as pd
from ._make_names_file import escapes
from pandas.api.types import is_string_dtype


def make_data_file(x, y, w=None):
    convert = {col: is_string_dtype(x[col]) for col in x}

    if True in convert.values():
        for col, value in convert.items():
            if value:
                x[col] = escapes(x[col].astype(str))
    # unclear if this needs to be implemented in Python:
    # if y.isnull().all():
    #     y = escapes()
    # if (is.null(y))
    #     y < - rep(NA_real_, nrow(x))
    y = escapes(y.astype(str))
    x = pd.concat([x, y], axis=1, ignore_index=True)
    if w is not None:
        x = pd.concat([x, w], axis=1, ignore_index=True)
    na_index = {}
    # Determine the locations of missing values

    return x
