import pandas as pd
import numpy as np


def _format(x: float, digits: int = 15) -> str:
    """Python version of the R format function to return a number formatted as a
    string rounded to `digits` number of digits from the left."""
    # if x is NA return NA
    if pd.isna(x):
        return x
    if np.iscomplex(x):
        raise ValueError("Complex numbers not supported")

    return np.format_float_positional(
        x, precision=digits, unique=False, fractional=False, trim="-"
    )
