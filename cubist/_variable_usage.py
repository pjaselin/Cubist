import pandas as pd


def get_variable_usage(output, x):
    output = output.split("\n")
    start_vars = [i for i, c in enumerate(output) if '\tAttribute usage' in c]
    if len(start_vars) != 1:
        raise ValueError("cannot find attribute usage data")
    output = output[start_vars[0]:(len(output))-2]
    output = [c.replace("\t", "") for c in output]
    has_pct = [i for i, c in enumerate(output) if "%" in c]
    if len(has_pct) < 1:
        return None
    output = [output[i] for i in has_pct]
    values = [get_values(c) for c in output]
    values = pd.DataFrame(values, columns=["Conditions", "Model"])
    values["Variable"] = [get_variable(c) for c in output]

    if values.shape[0] < x.shape[1]:
        x_names = set(x.columns)
        u_names = set(values["Variable"]) if values is not None else set()
        missing_vars = list(x_names - u_names)
        if missing_vars:
            zero_list = [0] * len(missing_vars)
            usage2 = pd.DataFrame({"Conditions": zero_list,
                                   "Model": zero_list,
                                   "Variable": missing_vars})
            values = pd.concat([values, usage2], axis=1)
            values = values.reset_index(drop=True)
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


def get_variable(x):
    x = x.split(" ")
    return x[-1]
