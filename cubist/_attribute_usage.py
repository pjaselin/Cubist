"""functions for parsing the 'Attribute usage' section of the Cubist model output"""

import pandas as pd


def _attribute_usage(output: str, feature_names: list | set):
    # split output at newline character
    output = output.split("\n")
    # convert feature_names to set
    feature_names = set(feature_names)
    # get the attribute usage section of the model output
    start_vars = [i for i, c in enumerate(output) if "\tAttribute usage" in c]
    # if not present raise an error
    if len(start_vars) != 1:
        raise ValueError("Cannot find attribute usage data")
    output = output[start_vars[0] : (len(output)) - 2]
    output = [c.replace("\t", "") for c in output]
    has_pct = [i for i, c in enumerate(output) if "%" in c]
    if len(has_pct) < 1:
        return None
    output = [output[i] for i in has_pct]
    values = [_get_values(c) for c in output]
    values = pd.DataFrame(values, columns=["Conditions", "Model"])
    values["Variable"] = [_get_variable(c) for c in output]

    if values.shape[0] < len(feature_names):
        u_names = set(values["Variable"]) if values is not None else set()
        if missing_vars := list(feature_names - u_names):
            zero_list = [0] * len(missing_vars)
            usage2 = pd.DataFrame(
                {"Conditions": zero_list, "Model": zero_list, "Variable": missing_vars}
            )
            values = pd.concat([values, usage2], axis=0)
            values = values.reset_index(drop=True)
    return values


def _get_values(x):
    x2 = x.split(" ")
    has_pct = ["%" in c for c in x2]
    if sum(has_pct) == 2:
        x2 = [x2[i] for i, c in enumerate(has_pct) if c]
        x2 = [float(c.replace("%", "")) for c in x2]
        return x2
    if sum(has_pct) == 1:
        pct_ind = [i for i, c in enumerate(x2) if "%" in c][0]
        if x2[1 : pct_ind + 1].count("") < x2[pct_ind + 1 :].count(""):
            x2 = [c for c in x2 if "%" in c][0]
            x2 = float(x2.replace("%", ""))
            return [x2, 0]
        x2 = [c for c in x2 if "%" in c][0]
        x2 = float(x2.replace("%", ""))
        return [0, x2]
    return 0


def _get_variable(x):
    return x.split(" ")[-1]
