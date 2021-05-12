from random import randint
import numpy as np
import pandas as pd
import warnings
from ._make_names_file import make_names_file
from ._make_data_file import make_data_file
# from . import _cubist as cubist


def cubist_control(unbiased: bool = False,
                   rules: int = 100,
                   extrapolation: int = 100,
                   sample: float = 0.0,
                   seed=randint(0, 4095),
                   label: str = "outcome"):
    if rules is not None and (rules < 1 or rules > 1000000):
        raise ValueError("number of rules must be between 1 and 1000000")
    if extrapolation < 0 or extrapolation > 100:
        raise ValueError("percent extrapolation must be between 0 and 100")
    if sample < 0.0 or sample > 99.9:
        raise ValueError("sampling percentage must be between 0.0 and 99")
    return dict(
        unbiased=unbiased,
        rules=rules,
        extrapolation=extrapolation / 100,
        sample=sample / 100,
        label=label,
        seed=seed % 4095  # TODO: this isn't right
    )


class Cubist:
    def __init__(self, x, y,
                 committees=1,
                 control=None,
                 weights=None,
                 **kwargs):
        if control is None:
            control = cubist_control()
        if not isinstance(y, (list, pd.Series, np.ndarray)):
            raise ValueError("cubist models require a numeric outcome")
        if committees < 1 or committees > 100:
            raise ValueError("number of committees must be between 1 and 100")
        if not isinstance(x, (pd.DataFrame, np.ndarray)):
            raise ValueError("x must be a Numpy Array or a Pandas DataFrame")
        if isinstance(x, np.ndarray):
            if len(x.shape) > 2:
                raise ValueError("Input NumPy array has more than two dimensions, "
                                 "only a two dimensional matrix may be passed.")
            else:
                warnings.warn("Input data is a NumPy Array, setting column names to default `var0, var1,...`.")
                x = pd.DataFrame(x, columns=[f'var{i}' for i in range(x.shape[1])])
        if weights is not None and not isinstance(weights, (list, np.ndarray)):
            raise ValueError("case weights must be numeric")

        names_string = make_names_file(x, y, w=weights, label=control["label"], comments=True)
        data_string = make_data_file(x, y, w=weights)

        # z = cubist(names_string,
        #            data_string,
        #            control["unbiased"],
        #            "yes",
        #            1,
        #            committees,
        #            control["sample"],
        #            control["seed"],
        #            control["rules"],
        #            control["extrapolation"],
        #            model="1",
        #            output="1")
        # Z < -.C("cubist",
        #     as.character(namesString),
        #     as.character(dataString),
        #     as.logical(control$unbiased),      # -u : generate unbiased rules
        #     "yes",                             # -i and -a : how to combine these?
        #     as.integer(1),                     # -n : set the number of nearest neighbors (1 to 9)
        #     as.integer(committees),            # -c : construct a committee model
        #     as.double(control$sample),         # -S : use a sample of x% for training
        #                                        #      and a disjoint sample for testing
        #     as.integer(control$seed),          # -I : set the sampling seed value
        #     as.integer(control$rules),         # -r: set the maximum number of rules
        #     as.double(control$extrapolation),  # -e : set the extrapolation limit
        #     model = character(1),              # pass back .model file as a string
        #     output = character(1),             # pass back cubist output as a string
        #     PACKAGE = "Cubist"
        #     )



