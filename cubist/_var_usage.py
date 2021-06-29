import pandas as pd


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
    values = pd.DataFrame(values, columns=["Conditions", "Model"])
    values["Variable"] = [get_var(c) for c in x]
    return values


def get_values(x):
    x2 = x.split(" ")
    has_pct = ["%" in c for c in x2]
    if sum(has_pct) == 2:
        x2 = [x2[i] for i, c in enumerate(has_pct) if c]
        x2 = [float(c.replace("%", "")) for c in x2]
        return x2
    else:
        if sum(has_pct) == 1:
            pct_ind = [i for i, c in enumerate(x2) if "%" in c][0]
            if x2[1:pct_ind+1].count("") < x2[pct_ind+1:].count(""):
                x2 = [c for c in x2 if "%" in c][0]
                x2 = float(x2.replace("%", ""))
                return [x2, 0]
            else:
                x2 = [c for c in x2 if "%" in c][0]
                x2 = float(x2.replace("%", ""))
                return [0, x2]
        else:
            return 0


def get_var(x):
    x = x.split(" ")
    return x[-1]
