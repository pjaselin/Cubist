"""functions for parsing the 'Attribute usage' section of the Cubist model output"""

import pandas as pd


def _attribute_usage(output: str, feature_names: list | set):
    # split output at newline character
    output = output.split("\n")
    # get the attribute usage section of the model output
    start_vars = [i for i, c in enumerate(output) if "\tAttribute usage" in c]
    # if not present raise an error
    if len(start_vars) != 1:
        raise ValueError("Cannot find attribute usage data")
    # keep only the Attribute usage section
    output = [o for o in output[start_vars[0] : (len(output)) - 2] if o != ""]
    # per line in the Attribute usage, remove the tabs and strip
    # leading/trailing whitespace
    output = [c.replace("\t", "").strip() for c in output]
    has_pct = [i for i, c in enumerate(output) if "%" in c]
    if len(has_pct) < 1:
        return None
    output = [output[i] for i in has_pct]
    values = [_get_values(c) for c in output]
    values = pd.DataFrame(values, columns=["Conditions", "Model"])
    # split on 4 whitespaces and use last element in the list as the variable
    values["Variable"] = [c.split("    ")[-1] for c in output]

    # check to see if there are more features than reported in the Attribute
    # usage table
    if values.shape[0] < len(feature_names):
        # get the list of missing features
        missing_vars = list(set(feature_names) - set(values.Variable))
        # create a list of zeros equal to the length of missing_vars
        zero_list = [0] * len(missing_vars)
        # create a dataframe of zeros for the Conditions and Model columns for
        # each missing variable and append to values
        values = pd.concat(
            [
                values,
                pd.DataFrame(
                    {
                        "Conditions": zero_list,
                        "Model": zero_list,
                        "Variable": missing_vars,
                    }
                ),
            ],
            axis=0,
        )
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
