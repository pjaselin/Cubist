from typing import ValuesView


def var_usage(x):
    x = x.split("\n")
    start_vars = [i for i, c in enumerate(x) if '\tAttribute usage' in c]
    if len(start_vars) != 1:
        raise ValueError("cannot find attribute usage data")
    x = x[start_vars[0]:(len(x))-2]
    x = [c.replace("\t", "") for c in x]
    has_pct = [i for i, c in enumerate(x) if "%" in c]
    if len(has_pct) < 1:
        return None
    x = [x[i] for i in has_pct]
    values = [get_values(c) for c in x]

    return


def get_values(x):
    x2 = x.split(" ")
    
    has_pct = ["%" in c for c in x2]
    if sum(has_pct) == 2:
        x2 = [x2[i] for i, c in has_pct if c] 
        x2 = [c.replace("%", "") for c in x2]


    print(x2)
    return


def get_var(x):
    return
