from multipledispatch import dispatch
import pandas as pd


@dispatch((pd.Float64Dtype, pd.Float32Dtype, pd.Int64Dtype, float, int))
def quinlan_attributes(x):
    return "continuous."


@dispatch(pd.StringDtype)
def quinlan_attributes(x):
    return f"{','.join(set(x))}."


@dispatch(pd.DataFrame)
def quinlan_attributes(x):
    return [quinlan_attributes(col_data) for col_name, col_data in x.iteritems()]
    # return x.apply(quinlan_attributes, axis=1)


@dispatch(pd.Series)
def quinlan_attributes(x):
    return "test"
