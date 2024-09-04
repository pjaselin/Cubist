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


def _parse_model(model: str, x, feature_names: list):
    # split on newline
    model = deque(model.split("\n"))
    # get the cubist model version and build date
    version = _parser(model.popleft())[0]["id"]
    # get the global model statistics
    model_statistics = {
        k: v for stat in _parser(model.popleft()) for k, v in stat.items()
    }
    # get the feature statistics
    feature_statistics = []
    while model[0].startswith("att="):
        feature_statistics.append(_parser(model.popleft()))
    # feature_statistics = None
    feature_statistics = pd.DataFrame(
        [{k: v for d in feat for k, v in d.items()} for feat in feature_statistics]
    )
    # get the number of committees
    committee_meta = _parser(model.popleft())
    # set default committee error reduction and number of committees
    committee_error_reduction = None
    n_committees = None
    for val in committee_meta:
        if "redn" in val:
            committee_error_reduction = float(val["redn"])  # noqa F841
        if "entries" in val:
            n_committees = int(val["entries"])  # noqa F841

    # clean out empty strings
    model = [m for m in model if m.strip() != ""]

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
        # there is only one rule
        splits = pd.DataFrame()
    else:
        splits = pd.DataFrame(
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
        splits = splits.dropna(subset=["variable"]).reset_index(drop=True)

        # get the percentage of data covered by this rule
        nrows = x.shape[0]
        for i in range(splits.shape[0]):
            # get the current value threshold and comparison operator
            var_value = splits.loc[i, "value"]
            comp_operator = splits.loc[i, "dir"]
            if (var_value is not None) and (not math.isnan(var_value)):
                # convert the data to numeric and remove NaNs
                x_col = pd.to_numeric(x[splits.loc[i, "variable"]]).dropna()
                # evaluate and get the percentage of data
                comp_total = OPERATORS[comp_operator](x_col, var_value).sum()
                splits.loc[i, "percentile"] = comp_total / nrows

    # get the indices of rows in model that contain model coefficients
    is_eqn = [i for i, c in enumerate(model) if c.startswith("coeff=")]
    # extract the model coefficients from the row
    coeffs = [_eqn(model[i], var_names=feature_names) for i in is_eqn]
    coeffs = pd.DataFrame(coeffs)
    # get the committee number
    coeffs["committee"] = [com_num[i] for i in is_eqn]
    # get the rule number for the committee
    coeffs["rule"] = [rule_num[i] for i in is_eqn]

    return (
        version,
        splits,
        coeffs,
        model_statistics,
        feature_statistics,
        committee_error_reduction,
        n_committees,
    )


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


def _eqn(x, var_names: list):
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

    # handle column headers
    vars2 = [var for var in var_names if var not in nms]
    vals2 = [np.nan] * len(vars2)
    vals2 = dict(zip(vars2, vals2))
    vals = {**vals, **vals2}
    new_names = ["(Intercept)"] + var_names
    vals = {nm: vals[nm] for nm in new_names}
    return vals


def _make_parsed_dict(x):
    x = x.split("=")
    return {x[0]: x[1].strip('"')}


def _parser(x):
    x = x.split('" ')
    x = [_make_parsed_dict(c) for c in x]
    return x
