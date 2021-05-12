from ._make_names_file import escapes
from pandas.api.types import is_string_dtype


def make_data_file(x, y, w=None):
    convert = {col: is_string_dtype(x[col]) for col in x}

    if True in convert.values():
        for col in convert:
            x[col] = escapes(x[col].astype(str))
    if y.isnull().all():
        y = escapes()
    return x
