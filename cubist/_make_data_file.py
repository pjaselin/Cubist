import pandas as pd
from ._make_names_file import escapes
from pandas.api.types import is_string_dtype, is_numeric_dtype, is_datetime64_any_dtype


def _format(x, digits=15):
    num_whole_nums = len(str(int(x)))
    # case where there are decimal places that need to be rounded
    if num_whole_nums < digits:
        remaining_decimals = digits - num_whole_nums
        return str(round(x, remaining_decimals))
    # case where there are no decimals that need to/can be rounded
    else:
        return str(x)


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

    # convert all columns to strings
    for col in x:
        if is_string_dtype(x[col]):
            continue
        if is_numeric_dtype(x[col]):
            x[col] = [_format(i) for i in x[col]]
            x[col] = x[col].astype(str)
        if is_datetime64_any_dtype(x[col]):
            x[col] = x[col].astype(str)

    # remove leading whitespace
    x = x.applymap(lambda a: a.lstrip())

    # Determine the locations of missing values
    na_index = {col: x[x[col].isnull()].index.tolist() for col in x}

    # reset missing values
    if any(len(l) > 0 for l in na_index.values()):
        for i, col in enumerate(na_index):
            print(i)

    return x

