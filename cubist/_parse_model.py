import re
import math 

import pandas as pd
import numpy as np


def split_to_groups(x, f):
    """Function to convert two lists into a dictionary where the keys are unique values in f and 
    the values are lists of the corresponding values in x. Analogous to the split function in R."""
    if len(x) != len(f):
        raise ValueError("lists x and f must be of the same length")
    groups = {}
    for a, b in zip(x, f):
        if b in groups:
            groups[b].append(a)
        else:
            groups[b] = [a]
    return groups


def parse_model(model, x):
    # split on newline
    model = model.split("\n")
    # remove empty strings
    model = [c for c in model if c.strip() != '']
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
        tt = parser(row)
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
    is_type2 = [i for i, c in enumerate(model) if re.search("^type=\"2\"", c)]
    for i in is_type2:
        # set the type of split
        split_type[i] = "continuous"
        continuous_split = type2(model[i])
        # set split variable name
        split_var[i] = continuous_split["var"].replace('\"', "")
        # set split direction (comparison operator)
        split_dir[i] = continuous_split["result"]
        # set split value
        split_val[i] = continuous_split["val"]

    # handle categorical (type 3) rules
    is_type3 = [i for i, c in enumerate(model) if re.search("^type=\"3\"", c)]
    for i in is_type3:
        categorical_split = type3(model[i])
        # set the type of split
        split_type[i] = "categorical"
        # set the split variable
        split_var[i] = categorical_split["var"]
        # set the split value
        split_cats[i] = categorical_split["val"]

    # if there are no continuous or categorical splits, return no splits
    if is_type2 == [] and is_type3 == []:
        split_data = None
    else:
        split_data = pd.DataFrame({
            "committee": com_num,
            "rule": rule_num,
            "variable": split_var,
            "dir": split_dir,
            "value": split_val,
            "category": split_cats,
            "type": split_type
        })
        # remove missing values based on the variable column
        split_data = split_data.dropna(subset=['variable'])
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
                    split_data.loc[i, "percentile"] = sum([eval(f"{c} {comp_operator} {var_value}") for c in x_col]) / nrows
    
    # get the indices of rows in model that contain model coefficients
    is_eqn = [i for i, c in enumerate(model) if "coeff=" in c]
    # extract the model coefficients from the row
    coefs = [eqn(model[i], var_names=list(x.columns)) for i in is_eqn]
    out = pd.DataFrame(coefs)
    # get the committee number
    out["committee"] = [com_num[i] for i in is_eqn]
    # get the rule number for the committee
    out["rule"] = [rule_num[i] for i in is_eqn]

    # get the value for maxd
    tmp = [c for c in model if "maxd" in c][0]
    tmp = tmp.split("\"")
    maxd_i = [i for i, c in enumerate(tmp) if "maxd" in c][0]
    maxd = tmp[maxd_i + 1]
    return split_data, out, float(maxd)


def type2(x, dig=3):
    x = x.replace("\"", "")

    # get the indices where these keywords start
    att_ind = x.find("att=")
    cut_ind = x.find("cut=")
    result_ind = x.find("result=")
    val_ind = x.find("val=")

    missing_rule = cut_ind < 1 and val_ind > 0
    if missing_rule:
        var = x[att_ind + 4:cut_ind - 1]
        val = None
        result = "="
    else:
        var = x[att_ind + 4:cut_ind - 1]
        val = x[cut_ind + 4:result_ind - 1]
        val = round(float(val), dig)
        result = x[result_ind + 7:]
    return {"var": var,
            "val": val,
            "result": result,
            "text": f"{var} {result} {val}"}


def type3(x):
    # get the indices where these keywords start
    att_ind = x.find("att=")
    elts_ind = x.find("elts=")

    var = x[att_ind + 5:elts_ind - 2]
    val = x[elts_ind + 5:]
    val = val.replace("[{}]", "").replace("\"", "").replace(" ", "").replace(",", ", ")

    # if there are multiple values in the categorical split, just show 
    # {multiple_vals} for cleaner printing}
    # TODO: enter all vals in dataframe but limit the column width when printing
    multiple_vals = "," in val
    if multiple_vals:
        val = f"{{multiple_vals}}"
        txt = f"{var} in {val}"
    else:
        txt = f"{var} = {val}"
    return {"var": var, "val": val, "text": txt}


def eqn(x, var_names=None):
    x = x.replace("\"", "")
    starts = [m.start(0) for m in re.finditer("(coeff=)|(att=)", x)]
    tmp = [""] * len(starts)
    for i in range(len(starts)):
        if i < len(starts) - 1:
            txt = x[starts[i]:starts[i + 1] - 1]
        else:
            txt = x[starts[i]:]
        tmp[i] = txt.replace("coeff=", "").replace("att=", "")

    vals = tmp[::2]
    vals = [float(c) for c in vals]
    nms = tmp[1::2]
    nms = ["(Intercept)"] + nms
    vals = {nm: val for nm, val in zip(nms, vals)}
    if var_names:
        vars2 = [var for var in var_names if var not in nms]
        vals2 = [np.nan] * len(vars2)
        vals2 = {nm: val for nm, val in zip(vars2, vals2)}
        vals = {**vals, **vals2}
        new_names = ["(Intercept)"] + var_names
        vals = {nm: vals[nm] for nm in new_names}
    return vals


def make_parsed_dict(x):
    x = x.split("=")
    if len(x) > 1:
        return {x[0]: x[1]}
    else:
        return None


def parser(x):
    x = x.split(" ")
    x = [make_parsed_dict(c) for c in x]
    return x
