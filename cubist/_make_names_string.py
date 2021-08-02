import re
import sys
from datetime import datetime

from ._quinlan_attributes import quinlan_attributes


def make_names_string(x, w=None, label="outcome"):
    """
    Create the names string to pass to Cubist. This string contains information about Python and the time of run along
    with the column names and their data types.

    Parameters
    ----------
    x : {pd.DataFrame} of shape (n_samples, n_features)
        The input samples.

    w : ndarray of shape (n_samples,)
        Instance weights.
    
    label : str, default="outcome"
        A label for the outcome variable. This is only used for printing rules.

    Returns
    -------
    out : str
        Case name string describing training dataset columns and their types.
    """
    # copy Pandas objects so they aren't changed outside of this function
    x = x.copy(deep=True)

    # clean reserved sample name if it's in x
    has_sample = [i for i, c in enumerate(x.columns) if bool(re.search('^sample', c))]
    if has_sample:
        x.columns = [re.sub('^sample', '_Sample', c) for c in x.columns]

    # generate the comments string showing the Python version and current timestamps
    python_version = tuple(sys.version_info)
    now = datetime.now()
    out = f'| Generated using Python {python_version[0]}.{python_version[1]}.{python_version[2]}\n' \
          f'| on {now.strftime("%a %b %d %H:%M:%S %Y")}'

    # define the outcome data type
    outcome_type = ": continuous."

    # build base out string
    out = f'{out}\n{label}.\n{label}{outcome_type}'

    # get dictionary of feature names as keys and data types as values
    var_data = quinlan_attributes(x)

    # if weights are present add this to var_data
    if w is not None:
        var_data["case weight"] = "continuous."

    # join the column names and data types into a single string
    var_data = [f'{escapes([key])[0]}: {value}' for key, value in var_data.items()]
    var_data = '\n'.join(var_data)

    # merge the out and var_data strings
    out = f'{out}\n{var_data}\n'
    return out


def escapes(x, chars=None):
    """Double escape reserved and special characters in x."""
    # set custom reserved characters list
    if chars is None:
        chars = [':', ';', '|']
    # apply first escaping
    for i in chars:
        x = [c.replace(i, f'\\{i}') for c in x]
    # apply second escaping
    x = [re_escape(c) for c in x]
    return x


_special_chars_map = {i: '\\' + chr(i) for i in b'()[]{}?*+-|:;^$\\.&~#\t\n\r\v\f'}


def re_escape(pattern):
    """Escape special characters in a string. Sourced from 're' Python package."""
    if isinstance(pattern, str):
        return pattern.translate(_special_chars_map)
    else:
        pattern = str(pattern, 'latin1')
        return pattern.translate(_special_chars_map).encode('latin1')
