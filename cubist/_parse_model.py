import re
import math
import operator
from collections import deque

import pandas as pd
import numpy as np

from ._utils import _format


OPERATORS = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
}


def _split_to_groups(x, f):
    """Function to convert two lists into a dictionary where the keys are
    unique values in f and the values are lists of the corresponding values in
    x. Analogous to the split function in R."""
    if len(x) != len(f):
        raise ValueError("lists x and f must be of the same length")
    groups = {}
    for a, b in zip(x, f):
        if b in groups:
            groups[b].append(a)
        else:
            groups[b] = [a]
    return groups


def _parse_model(model, x):
    # split on newline
    print(model)
    model = deque(model.split("\n"))

    # get the cubist model version and build date
    cubist_version = model.popleft()  # noqa F841
    # get the global model statistics
    global_stats = model.popleft()  # noqa F841
    # get the attribute statistics
    attribute_statistics = []
    while model[0].startswith("att="):
        attribute_statistics.append(model.popleft())
    # get the number of committees
    committee_meta = model.popleft()
    i_entries = committee_meta.find("entries")
    # get the error reduction from using committees
    if committee_meta.startswith("redn"):
        error_reduction = float(committee_meta[5:i_entries].strip().strip('"'))  # noqa F841
    else:
        error_reduction = None  # noqa F841
    num_committees = int(committee_meta[i_entries + 8 :].strip('"'))
    print(num_committees)

    # clean out empty strings
    model = [m for m in model if m.strip() != ""]

    # parse rules by committee
    com_idx = 0
    rules_idx = 1  # noqa F841
    num_rules = 0  # noqa F841
    for line in model:
        # a committe entry startswith a rule count
        if line.startswith("rules"):
            com_idx += 1
            rules_idx = 1  # noqa F841
            print(_parser2(line))
            num_rules = int(_parser2(line)["rules"])  # noqa F841
        # rule stats
        if line.startswith("conds"):
            pass
        # parse rule info
        if line.startswith("coeff"):
            print(_parser2(line))

    # get model length
    model_len = len(model)

    # define initial lists and index variables
    com_num = [None] * model_len
    rule_num = [None] * model_len
    cond_num = [None] * model_len
    com_idx = r_idx = 0

    # loop through model and indicate
    for i, row in enumerate(model):
        # break each row of x into dicts for each key/value pair
        tt = _parser(row)
        # get the first key in the first entry of tt
        first_key = list(tt[0])[0]

        # start of a new committee and rule
        if first_key == "rules":
            # increment committee number
            com_idx += 1
            # reset rule number
            r_idx = 0
        # set the current committee number
        com_num[i] = com_idx
        # start of a new rule
        if first_key == "conds":
            # increment rule number
            r_idx += 1
            # reset condition number
            c_idx = 0
        # set the current rule number
        rule_num[i] = r_idx
        # within a rule, type designates the type of conditional statement
        # type = 2 appears to be a simple split of a continuous predictor
        if first_key == "type":
            # increment condition number
            c_idx += 1
            # set the current condition number
            cond_num[i] = c_idx

    split_var = [None] * model_len
    split_val = [None] * model_len
    split_cats = [""] * model_len
    split_dir = [""] * model_len
    split_type = [""] * model_len
    print("model", model, len(model))
    # handle continuous (type 2) rules
    is_type2 = [i for i, c in enumerate(model) if re.search('^type="2"', c)]
    for i in is_type2:
        # set the type of split
        split_type[i] = "continuous"
        continuous_split = _type2(model[i])
        # set split variable name
        split_var[i] = continuous_split["var"].replace('"', "")
        # set split direction (comparison operator)
        split_dir[i] = continuous_split["result"]
        # set split value
        split_val[i] = continuous_split["val"]

    # handle categorical (type 3) rules
    is_type3 = [i for i, c in enumerate(model) if re.search('^type="3"', c)]
    for i in is_type3:
        categorical_split = _type3(model[i])
        # set the type of split
        split_type[i] = "categorical"
        # set the split variable
        split_var[i] = categorical_split["var"]
        # set the split value
        split_cats[i] = categorical_split["val"]

    # if there are no continuous or categorical splits, return no splits
    if not is_type2 and not is_type3:
        split_data = None
    else:
        split_data = pd.DataFrame(
            {
                "committee": com_num,
                "rule": rule_num,
                "variable": split_var,
                "dir": split_dir,
                "value": split_val,
                "category": split_cats,
                "type": split_type,
            }
        )
        # remove missing values based on the variable column
        split_data = split_data.dropna(subset=["variable"])
        split_data = split_data.reset_index(drop=True)

        # get the percentage of data covered by this rule
        nrows = x.shape[0]
        for i in range(split_data.shape[0]):
            # get the current value threshold and comparison operator
            var_value = split_data.loc[i, "value"]
            comp_operator = split_data.loc[i, "dir"]
            if var_value is not None:
                if not math.isnan(var_value):
                    # convert the data to numeric and remove NaNs
                    x_col = pd.to_numeric(x[split_data.loc[i, "variable"]]).dropna()
                    # evaluate and get the percentage of data
                    comp_total = OPERATORS[comp_operator](x_col, var_value).sum()
                    split_data.loc[i, "percentile"] = comp_total / nrows

    # get the indices of rows in model that contain model coefficients
    is_eqn = [i for i, c in enumerate(model) if "coeff=" in c]
    # extract the model coefficients from the row
    coeffs = [_eqn(model[i], var_names=list(x.columns)) for i in is_eqn]
    coeffs = pd.DataFrame(coeffs)
    # get the committee number
    coeffs["committee"] = [com_num[i] for i in is_eqn]
    # get the rule number for the committee
    coeffs["rule"] = [rule_num[i] for i in is_eqn]

    return split_data, coeffs  # rules, coefficients


def _type2(x, dig=3):
    x = x.replace('"', "")

    # get the indices where these keywords start
    att_ind = x.find("att=")
    cut_ind = x.find("cut=")
    result_ind = x.find("result=")
    val_ind = x.find("val=")

    missing_rule = cut_ind < 1 and val_ind > 0
    if missing_rule:
        var = x[att_ind + 4 : cut_ind - 1]
        val = None
        result = "="
    else:
        var = x[att_ind + 4 : cut_ind - 1]
        val = x[cut_ind + 4 : result_ind - 1]
        val = _format(float(val), dig)
        result = x[result_ind + 7 :]
    return {
        "var": var,
        "val": float(val),
        "result": result,
        "text": f"{var} {result} {val}",
    }


def _type3(x):
    # get the indices where these keywords start
    att_ind = x.find("att=")
    elts_ind = x.find("elts=")

    var = x[att_ind + 5 : elts_ind - 2]
    val = x[elts_ind + 5 :]
    val = val.replace("[{}]", "").replace('"', "").replace(" ", "").replace(",", ", ")

    # if there are multiple values in the categorical split, just show
    # {multiple_vals} for cleaner printing}
    # TODO: enter all vals in dataframe but limit the column width when printing
    multiple_vals = "," in val
    if multiple_vals:
        val = "{" + str(multiple_vals) + "}"
        txt = f"{var} in {val}"
    else:
        txt = f"{var} = {val}"
    return {"var": var, "val": val, "text": txt}


def _eqn(x, var_names=None):
    x = x.replace('"', "")
    starts = [m.start(0) for m in re.finditer("(coeff=)|(att=)", x)]
    tmp = [""] * len(starts)
    for i, val in enumerate(starts):
        if i < len(starts) - 1:
            txt = x[val : starts[i + 1] - 1]
        else:
            txt = x[val:]
        tmp[i] = txt.replace("coeff=", "").replace("att=", "")

    vals = tmp[::2]
    vals = [float(c) for c in vals]
    nms = tmp[1::2]
    nms = ["(Intercept)"] + nms
    vals = dict(zip(nms, vals))
    if var_names:
        vars2 = [var for var in var_names if var not in nms]
        vals2 = [np.nan] * len(vars2)
        vals2 = dict(zip(vars2, vals2))
        vals = {**vals, **vals2}
        new_names = ["(Intercept)"] + var_names
        vals = {nm: vals[nm] for nm in new_names}
    return vals


def _make_parsed_dict(x):
    x = x.split("=")
    if len(x) > 1:
        return {x[0]: x[1].strip('"')}
    return None


def _parser(x):
    x = x.split(" ")
    x = [_make_parsed_dict(c) for c in x]
    return x


def _parse_element(x):
    # split the element on the equal sign and return without the quotes on the
    # value of the element
    label, value = x.split("=")
    return (label, value.strip('"'))


def _parser2(x):
    """Parses a row of the Cubist model string
    Takes: redn="0.967" entries="3"
    and converts to: {"redn": "0.967", "entries": "3"}
    """
    # split on the space separating each element in the rule
    x = x.split(" ")
    # create dictionary key value pairs for each element in the rule
    return dict([_parse_element(entry) for entry in x])
