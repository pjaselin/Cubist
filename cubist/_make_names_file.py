import re
import sys
from datetime import datetime
from ._quinlan_attributes import quinlan_attributes


def make_names_file(x, y, w=None, label="outcome", comments=True):
    has_sample = [i for i, c in enumerate(x.columns) if bool(re.search('^sample', c))]
    if has_sample:
        x.columns = [re.sub('^sample', '_Sample', c) for c in x.columns]

    if comments:
        python_version = tuple(sys.version_info)
        now = datetime.now()
        out = f'| Generated using Python {python_version[0]}.{python_version[1]}.{python_version[2]}\n' \
              f'| on {now.strftime("%a %b %d %H:%M:%S %Y")}'
    else:
        out = ""

    outcome_info = ": continuous."

    out = f'{out}\n{label}.\n{label}{outcome_info}'

    var_data = quinlan_attributes(x)

    if w is not None:
        var_data["case weight"] = "continuous."

    var_data = [f'{escapes([key])[0]}: {value}' for key, value in var_data.items()]
    var_data = '\n'.join(var_data)

    out = f'{out}\n{var_data}\n'
    return out


def escapes(x, chars=None):
    if chars is None:
        chars = [':', ';', '|']
    for i in chars:
        x = [c.replace(i, f'\\{i}') for c in x]
    x = [_re_escape(c) for c in x]
    return x


_special_chars_map = {i: '\\' + chr(i) for i in b'()[]{}?*+-|:;^$\\.&~#\t\n\r\v\f'}


def _re_escape(pattern):
    """
    Escape special characters in a string. Sourced from 're' Python package.
    """
    if isinstance(pattern, str):
        return pattern.translate(_special_chars_map)
    else:
        pattern = str(pattern, 'latin1')
        return pattern.translate(_special_chars_map).encode('latin1')
