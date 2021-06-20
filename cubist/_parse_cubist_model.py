import re
# import itertools


def count_rules(x):
    return

def split_to_groups(x, f):
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

    com_num = [None] * len(x)
    rule_num = [None] * len(x) 
    cond_num = [None] * len(x)
    com_idx, r_idx = 0, 0

    for i in range(len(x)):
        tt = parser(x[i])
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
    
    num_com = len([c for c in x if re.search("^rules=", c)])
    
    rules_per_com = split_to_groups(rule_num, com_num)
    rules_per_com = {a: max(rules_per_com[a]) for a in rules_per_com}
    rules_per_com = {a: rules_per_com[a] for a in rules_per_com if rules_per_com[a] > 0}
    if rules_per_com and num_com > 0:
        rules_per_com = {f'Com {i}': rules_per_com[a] for i, a in enumerate(list(rules_per_com.keys()))}
    
    is_new_rule = True if [c for c in x if re.search("^conds=", c)] else False

    split_var = [""] * len(x)
    split_val = [None] * len(x)
    split_cats = [""] * len(x)
    split_dir = [""] * len(x)
    
    is_type2 = [i for i, c in enumerate(x) if re.search("^type=\"2\"", c)]
    if is_type2:
        for i in is_type2:
            split_var[i] = type2(x[i])
    
    

    
    return

def type3(x):
    return

def type2(x):
    x = x.replace("\"", "")
    a_ind = x.find("att=")
    c_ind = x.find("cut=")
    r_ind = x.find("result=")
    v_ind = x.find("val=")

    var = [""] * len(x)
    val = [""] * len(x)
    rslt = [""] * len(x)
    # print(c_ind, a_ind, r_ind, v_ind)
    # missing_rule = [a and b for a, b in zip([c < 1 for c in c_ind], [v > 0 for v in v_ind])]
    missing_rule = c_ind < 1 and v_ind > 0
    if missing_rule:
        var[missing_rule] = None
    
    return

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