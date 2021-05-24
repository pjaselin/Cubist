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
    y = pd.Series(escapes(y.astype(str)))
    x["y"] = y
    if w is not None:
        column_names = list(x.columns) + [f"w{i}" for i in range(w.shape[1])]
        x = pd.concat([x, w], axis=1, ignore_index=True)
        x.columns = column_names
    # Determine the locations of missing values
    na_index = {col: x[x[col].isnull()].index.tolist() for col in x}
    any_na = any(len(l) > 0 for l in na_index.values())


    return x
