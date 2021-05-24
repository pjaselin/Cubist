from random import randint
import numpy as np
import pandas as pd
import warnings
from ._make_names_file import make_names_file
from ._make_data_file import make_data_file
# from . import _cubist as cubist


class Cubist:
    def __init__(self,
                 committees: int = 1,
                 unbiased: bool = False,
                 rules: int = 100,
                 extrapolation: int = 100,
                 sample: float = 0.0,
                 seed=randint(0, 4095), # TODO fix this since its different from R
                 label: str = "outcome",
                 weights=None,
                 **kwargs):
        assert committees > 1 or committees < 100, "number of committees must be between 1 and 100"
        self.committees = committees

        self.unbiased = unbiased

        assert rules is not None and (rules > 1 or rules < 1000000), "number of rules must be between 1 and 1000000"
        self.rules = rules

        assert extrapolation > 0 or extrapolation < 100, "percent extrapolation must be between 0 and 100"
        self.extrapolation = extrapolation / 100

        assert sample > 0.0 or sample < 99.9, "sampling percentage must be between 0.0 and 99"
        self.sample = sample / 100

        self.seed = seed % 4095

        self.label = label

        assert weights is None or isinstance(weights, (list, np.ndarray)), "case weights must be numeric"
        self.weights = weights

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

    def __repr__(self):
        return f'{self.__class__.__name__}(x, y, committees={self.committees}, unbiased={self.unbiased}, ' \
               f'rules={self.rules}, extrapolation={self.extrapolation}, sample={self.sample}, seed={self.seed}, ' \
               f'label={self.label}, weights)'

    def fit(self, x, y):
        assert isinstance(y, (list, pd.Series, np.ndarray)), "cubist models require a numeric outcome"
        if not isinstance(y, pd.Series):
            y = pd.Series(y)

        assert isinstance(x, (pd.DataFrame, np.ndarray)), "x must be a Numpy Array or a Pandas DataFrame"
        if isinstance(x, np.ndarray):
            assert len(x.shape) > 2, "Input NumPy array has more than two dimensions, only a two dimensional matrix " \
                                     "may be passed."
            warnings.warn("Input data is a NumPy Array, setting column names to default `var0, var1,...`.")
            x = pd.DataFrame(x, columns=[f'var{i}' for i in range(x.shape[1])])

        x = x.reset_index(drop=True)
        y = y.reset_index(drop=True)

        names_string = make_names_file(x, y, w=self.weights, label=self.label, comments=True)
        data_string = make_data_file(x, y, w=self.weights)
