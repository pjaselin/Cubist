import re
import sys
from datetime import datetime
import pandas as pd
import numpy as np
from .quinlan_attributes import quinlan_attributes


def is_sorted(l):
    if all(l[i] <= l[i+1] for i in range(len(l)-1)):
        return True
    else:
        return False


def make_names_file(x, y, w=None, label="outcome", comments=True):
    has_sample = [i for i, c in x.columns if bool(re.search('^sample', c))]
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
    # if not isinstance(y, (list, pd.Series, np.ndarray)):
    #     outcome_info = ": continuous."
    # else:
    #     lvls = escapes(list(set(y)))
    #     prefix = "[ordered]" if is_sorted(y) else ""
    #     outcome_info = f': {prefix} {",".join(lvls)} .'

    out = f'{out}\n{label}.\n{label}{outcome_info}'
    var_data = quinlan_attributes(x)

    if w is None:
        var_data = [var_data]


def escapes(x, chars=None):
    if chars is None:
        chars = [':', ';', '|']
    for i in chars:
        x = [c.replace(i, f'\\{i}') for c in x]
    print(x)
    for c in x:
        # print(re.sub(r'[^A-Za-z0-9 ]+', r'\\\\\\1', c))
        print(re.match(b'[^0-9a-zA-Z]+', c))
        # print(re.sub(r'[^0-9a-zA-Z ]', r'\\\\\\1', c))
    # return [re.sub('[^0-9a-zA-Z]', '\\\\\\1', c) for c in x]


# escapes(["1:|", "4|:;", "asd ", "a:"])
