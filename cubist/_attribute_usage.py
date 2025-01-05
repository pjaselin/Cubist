"""Functions for parsing the 'Attribute usage' section of the Cubist model output"""

import pandas as pd


def _attribute_usage(output: str, feature_names: list | set):
    """
    Function to convert the `Attribute usage` section of the Cubist output into
    a Pandas DataFrame.

    Parameters
    ----------
    output : str
        The Cubist verbose/pretty print summary of the trained model.

    feature_names : list | set
        The list of feature/attribute names used when training the model.

    Returns
    -------
    output : pd.DataFrame
        DataFrame of the variable/attribute usage in the conditions and linear
        models created by Cubist.
    """
    # get the attribute usage section of the model output
    start_i = output.find("Attribute usage:")
    # if not found raise error
    if start_i == -1:
        raise ValueError("Cannot find attribute usage data")
    # get the end index of the attribute usage section
    end_i = min(
        i
        for i in [output.find("Time: "), output.find("Evaluation on test data")]
        if i > 0
    )
    # filter output down to the string containing the attribute usage data
    output = output[start_i + 17 : end_i].rstrip("\n")
    # filter out empty strings
    output = [o for o in output.split("\n") if o != ""]
    # remove the first element as this is the column headers
    output.pop(0)

    # per line in the attribute usage, parse the percentages and attribute name
    output = [_parse_attribute(o.lstrip("\t").strip()) for o in output]
    # create dataframe
    output = pd.DataFrame(output, columns=["Conditions", "Model", "Variable"])
    # check to see if there are more features than reported in the attribute
    # usage table
    if output.shape[0] < len(feature_names):
        # get the list of missing features
        missing_vars = list(set(feature_names) - set(output.Variable))
        # create a list of zeros equal to the length of missing_vars
        zero_list = [0.0] * len(missing_vars)
        # create a dataframe of zeros for the Conditions and Model columns for
        # each missing variable and append to values
        missing_vars_df = pd.DataFrame(
            {
                "Conditions": zero_list,
                "Model": zero_list,
                "Variable": missing_vars,
            }
        )
        output = pd.concat([output, missing_vars_df], axis=0)
    return output


def _parse_attribute(x) -> list[float, float, str]:
    """Parse an attribute row from the attribute usage table and return as a
    list of [Condition, Model, Variable]"""
    # get the variable name as the string following the last occurrence of four
    # whitespace characters
    attribute_start_i = x.rindex("    ") + 4
    attribute_name = x[attribute_start_i:]
    return _get_values(x[:attribute_start_i]) + [attribute_name]


def _get_values(x) -> list[float, float]:
    """Takes the string containing the percentages of usage and assigns them to
    the conditions (index 0) or model (index 1), removes the % symbol and
    converts to a number"""
    x2 = x.split(" ")
    has_pct = ["%" in c for c in x2]
    if sum(has_pct) == 2:
        x2 = [x2[i] for i, c in enumerate(has_pct) if c]
        return [float(c.replace("%", "")) for c in x2]
    pct_ind = [i for i, c in enumerate(x2) if "%" in c][0]
    if x2[1 : pct_ind + 1].count("") < x2[pct_ind + 1 :].count(""):
        x2 = [c for c in x2 if "%" in c][0]
        x2 = float(x2.replace("%", ""))
        return [x2, 0.0]
    x2 = [c for c in x2 if "%" in c][0]
    x2 = float(x2.replace("%", ""))
    return [0.0, x2]
