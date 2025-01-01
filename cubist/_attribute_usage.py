"""functions for parsing the 'Attribute usage' section of the Cubist model output"""

import pandas as pd


def _attribute_usage(output: str, feature_names: list | set):
    # get the attribute usage section of the model output
    start_i = output.find("Attribute usage:")
    if start_i == -1:
        raise ValueError("Cannot find attribute usage data")
    end_i = min(
        i
        for i in [output.find("Time: "), output.find("Evaluation on test data")]
        if i > 0
    )

    output = output[start_i + 17 : end_i].rstrip("\n")

    # keep only the Attribute usage section
    output = [o for o in output.split("\n") if o != ""]
    columns = output.pop(0).lstrip("\t").strip().split("  ")

    # per line in the Attribute usage, remove the tabs and strip
    # leading/trailing whitespace
    output = [_parse_attribute(o.lstrip("\t").strip()) for o in output]
    # left pad output
    output = pd.DataFrame(output, columns=columns + ["Variable"])
    # check to see if there are more features than reported in the Attribute
    # usage table
    if output.shape[0] < len(feature_names):
        # get the list of missing features
        missing_vars = list(set(feature_names) - set(output.Variable))
        # create a list of zeros equal to the length of missing_vars
        zero_list = [None] * len(missing_vars)
        # create a dataframe of zeros for the Conditions and Model columns for
        # each missing variable and append to values
        output = pd.concat(
            [
                output,
                pd.DataFrame(
                    {
                        "Conds": zero_list,
                        "Model": zero_list,
                        "Variable": missing_vars,
                    }
                ),
            ],
            axis=0,
        )
    return output


def _parse_attribute(x):
    # get the variable name as the string following the last occurrence of four
    # whitespace characters
    attribute_start_i = x.rindex("    ")
    attribute_name = x[attribute_start_i:]
    return _get_values(x[:attribute_start_i]) + [attribute_name]


def _get_values(x) -> list[int, int]:
    x2 = x.split(" ")
    has_pct = ["%" in c for c in x2]
    if sum(has_pct) == 2:
        x2 = [x2[i] for i, c in enumerate(has_pct) if c]
        return [float(c.replace("%", "")) for c in x2]
    pct_ind = [i for i, c in enumerate(x2) if "%" in c][0]
    if x2[1 : pct_ind + 1].count("") < x2[pct_ind + 1 :].count(""):
        x2 = [c for c in x2 if "%" in c][0]
        x2 = float(x2.replace("%", ""))
        return [x2, 0]
    x2 = [c for c in x2 if "%" in c][0]
    x2 = float(x2.replace("%", ""))
    return [0, x2]
