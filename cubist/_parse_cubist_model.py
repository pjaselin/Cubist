import re
import pandas as pd

def count_rules(x):
    return

def split_to_groups(x, f):
    """Function to convert two lists into a dictionary where the keys are unique values in f and 
    the values are lists of the corresponding values in x. Analagous to the split function in R.

    :param x: Input list
    :param f: Input list
    :return: Formatting information about the Series
    """
    if len(x) != len(f):
        raise ValueError("lists x and f must be of the same length")
    groups = {}
    for a, b in zip(x, f):
        if b in groups:
            groups[b].append(a)
        else:
            groups[b] = [a]
    return groups

def get_splits(x):
    # split on newline
    x = x.split("\n")

    # remove empty strings
    x = [c for c in x if c.strip()]

    # define initial lists and index variables
    com_num = [None] * len(x)
    rule_num = [None] * len(x) 
    cond_num = [None] * len(x)
    com_idx, r_idx = 0, 0

    for i in range(len(x)):
        # break each row of x into dicts for each key/value pair
        tt = parser(x[i])
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
    num_com = len([c for c in x if re.search("^rules=", c)])
    
    rules_per_com = split_to_groups(rule_num, com_num)
    rules_per_com = {a: max(rules_per_com[a]) for a in rules_per_com}
    rules_per_com = {a: rules_per_com[a] for a in rules_per_com if rules_per_com[a] > 0}
    if rules_per_com and num_com > 0:
        rules_per_com = {f'Com {i+1}': rules_per_com[a] for i, a in enumerate(list(rules_per_com.keys()))}
    
    is_new_rule = [True if re.search("^conds=", c) else False for c in x]
    split_var = [None] * len(x)
    split_val = [None] * len(x)
    split_cats = [""] * len(x)
    split_dir = [""] * len(x)
    split_type = [""] * len(x)
    
    is_type2 = [i for i, c in enumerate(x) if re.search("^type=\"2\"", c)]
    if is_type2:
        for i in is_type2:
            split_type[i] = "type2"
            continuous_split = type2(x[i])
            split_var[i] = continuous_split["var"].replace('\"', "")
            split_dir[i] = continuous_split["rslt"]
            split_val[i] = continuous_split["val"]
    
    is_type3 = [i for i, c in enumerate(x) if re.search("^type=\"3\"", c)]
    if is_type3:
        for i in is_type3:
            split_type[i] = "type3"
            pass
    
    # print(split_var)
    # print(split_dir)
    # print(split_val)
    
    if not is_type2 and not is_type3:
        return None
    
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
    return split_data

# TODO: finish with categorical data
def type3(x):
    a_ind = x.find("att=")
    e_ind = x.find("elts=")
    var = x[a_ind+4:e_ind-2]
    val = x[e_ind+5:]
    mult_vals = None
    return

def type2(x, dig=3):
    x = x.replace("\"", "")
    a_ind = x.find("att=")
    c_ind = x.find("cut=")
    r_ind = x.find("result=")
    v_ind = x.find("val=")

    missing_rule = c_ind < 1 and v_ind > 0
    if missing_rule:
        var = x[a_ind+4:c_ind-1]
        val = None
        rslt = "="
    else:
        # print(x)
        var = x[a_ind+4:c_ind-1]
        val = x[c_ind+4:r_ind-1]
        val = round(float(val), dig)
        rslt = x[r_ind+7:]
    return {"var": var,
            "val": val,
            "rslt": rslt,
            "text": f"{var} {rslt} {val}"}

def get_percentiles(x_col, value, nrows):
    if value:
        return sum([c <= value for c in x_col]) / nrows

def eqn(x, dig=10, text=True, var_names=None):
    return

def make_parsed_dict(y):
    y = y.split("=")
    if len(y) > 1:
        return {y[0]: y[1]}
    else:
        return y

def parser(x):
    x = x.split(" ")
    x = [make_parsed_dict(c) for c in x]
    return x

def coef_cubist(x, var_names=None, *kwargs):
    return