import re

import pandas as pd
import numpy as np


def count_rules(x):
    return


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


def parse_cubist_model(model, x):
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
        first_key = list(tt[0].keys())[0]

        # start of a new rule
        if first_key == "rules":
            com_idx += 1
            r_idx = 0
        com_num[i] = com_idx
        # start of a new condition
        if first_key == "conds":
            r_idx += 1
            c_idx = 0
        rule_num[i] = r_idx
        # within a rule, type designates the type of conditional statement
        # type = 2 appears to be a simple split of a continuous predictor
        if first_key == "type":
            c_idx += 1
            cond_num[i] = c_idx
    
    # get the number of committees
    num_com = len([c for c in model if re.search("^rules=", c)])

    # apply the analogous R split function to get a dict
    rules_per_com = split_to_groups(rule_num, com_num)

    rules_per_com = {a: max(rules_per_com[a]) for a in rules_per_com}
    rules_per_com = {a: rules_per_com[a] for a in rules_per_com if rules_per_com[a] > 0}
    if rules_per_com and num_com > 0:
        rules_per_com = {f'Com {i + 1}': rules_per_com[a] for i, a in enumerate(list(rules_per_com.keys()))}
    
    split_var = [None] * model_len
    split_val = [None] * model_len
    split_cats = [""] * model_len
    split_dir = [""] * model_len
    split_type = [""] * model_len

    is_type2 = [i for i, c in enumerate(model) if re.search("^type=\"2\"", c)]
    for i in is_type2:
        split_type[i] = "type2"
        continuous_split = type2(model[i])
        split_var[i] = continuous_split["var"].replace('\"', "")
        split_dir[i] = continuous_split["rslt"]
        split_val[i] = continuous_split["val"]

    is_type3 = [i for i, c in enumerate(model) if re.search("^type=\"3\"", c)]
    for i in is_type3:
        categorical_split = type3(model[i])
        split_var[i] = categorical_split["var"]
        split_cats[i] = categorical_split["val"]

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
        split_data = split_data.dropna(subset=['variable'])
        split_data = split_data.reset_index(drop=True)

        # get the rule by rule percentiles (?)
        nrows = x.shape[0]
        for i in range(split_data.shape[0]):
            var = split_data.loc[i, "value"]
            if not np.isnan(var):
                x_col = pd.to_numeric(x[split_data.loc[i, "variable"]])
                split_data.loc[i, "percentile"] = sum([c <= var for c in x_col]) / nrows

    # get coefficients
    is_eqn = [i for i, c in enumerate(model) if "coeff=" in c]
    coefs = [eqn(model[i], var_names=list(x.columns)) for i in is_eqn]
    out = pd.DataFrame(coefs)
    out["committee"] = [com_num[i] for i in is_eqn]
    out["rule"] = [rule_num[i] for i in is_eqn]

    # get maxd
    tmp = [c for c in model if "maxd" in c][0]
    tmp = tmp.split("\"")
    maxd_i = [i for i, c in enumerate(tmp) if "maxd" in c][0]
    maxd = tmp[maxd_i + 1]
    return split_data, out, float(maxd)


def type3(x):
    a_ind = x.find("att=")
    e_ind = x.find("elts=")
    var = x[a_ind + 5:e_ind - 2]
    val = x[e_ind + 5:]
    val = val.replace("[{}]", "").replace("\"", "").replace(" ", "")
    mult_vals = "," in val
    val = val.replace(",", ", ")
    if mult_vals:
        val = f"{{mult_vals}}"
        txt = f"{var} in {val}"
    else:
        txt = f"{var} = {val}"
    return {"var": var, "val": val, "text": txt}


def type2(x, dig=3):
    x = x.replace("\"", "")
    a_ind = x.find("att=")
    c_ind = x.find("cut=")
    r_ind = x.find("result=")
    v_ind = x.find("val=")

    missing_rule = c_ind < 1 and v_ind > 0
    if missing_rule:
        var = x[a_ind + 4:c_ind - 1]
        val = None
        rslt = "="
    else:
        var = x[a_ind + 4:c_ind - 1]
        val = x[c_ind + 4:r_ind - 1]
        val = round(float(val), dig)
        rslt = x[r_ind + 7:]
    return {"var": var,
            "val": val,
            "rslt": rslt,
            "text": f"{var} {rslt} {val}"}


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
    """"""
    x = x.split("=")
    if len(x) > 1:
        return {x[0]: x[1]}
    else:
        return None


def parser(x):
    """"""
    x = x.split(" ")
    x = [make_parsed_dict(c) for c in x]
    return x
