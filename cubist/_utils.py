import pandas as pd
import numpy as np


def _format(x: float, digits: int = 15) -> str:
    """Python version of the R format function to return a number formatted as a
    string rounded to `digits` number of digits from the left."""
    # if x is NA or 0 return NA
    if pd.isna(x) or x == 0:
        return x
    if np.iscomplex(x):
        raise ValueError("Complex numbers not supported")

    return np.format_float_positional(
        x, precision=digits, unique=False, fractional=False, trim="-"
    )
