import math

import pandas as pd

try:
    from sklearn.utils._optional_dependencies import check_matplotlib_support
except ImportError:
    from sklearn.utils import check_matplotlib_support


class _CubistDisplayMixin:
    """Mixin class to be used in Displays for Cubist.

    The aim of this class is to centralize some validations for generating the matplotlib figure and axes as well as for processing the data to be plotted.
    """

    def _validate_plot_params(
        self, *, ax=None, df: pd.DataFrame = None, gridspec_kwargs: dict = None
    ):
        check_matplotlib_support(f"{self.__class__.__name__}.plot")
        import matplotlib.pyplot as plt

        if gridspec_kwargs is None:
            gridspec_kwargs = {}

        if ax is None:
            nplots = df.variable.nunique()
            nrows = ncols = int(round(math.sqrt(nplots)))
            if nplots > (nrows * ncols):
                nrows += 1
            fig, ax = plt.subplots(
                ncols=ncols,
                nrows=nrows,
                sharex="all",
                sharey="all",
                gridspec_kw=dict(hspace=0.5, wspace=0) | gridspec_kwargs,
            )
            ax = ax.reshape(-1)
        else:
            fig = plt.gcf()  # or ax.figure?
        return fig, ax

    @classmethod
    def _validate_from_estimator_params(
        cls, *, df: pd.DataFrame = None, committee: int = None, rule: int = None
    ):
        check_matplotlib_support(f"{cls.__name__}.from_estimator")

        # get rows that are continuous-type splits
        df = df.loc[df.type == "continuous"].reset_index(drop=True)

        # if none of the rows were continuous-type splits, break here
        if df.empty:
            raise ValueError(
                "No splits of continuous predictors were used in this model"
            )

        # if the committee parameter is passed
        if committee is not None:
            # verify committee parameter is integer
            if not isinstance(committee, int):
                raise TypeError(
                    f"`committee` must be an integer but got {type(committee)}"
                )
            # filter for committees below requested committee number
            df = df.loc[df.committee <= committee]

        # if rule parameter is passed
        if rule is not None:
            # verify rule parameter is integer
            if not isinstance(rule, int):
                raise TypeError(f"`rule` must be an integer but got {type(rule)}")
            # filter for rules below requested rule number
            df = df.loc[df.rule <= rule]

        if df.committee.max() == 1:
            # if there is only one committee, this is a rule-only model
            ylabel = "Rule"
            df["label"] = df.rule.astype(str).str.replace(" ", "0", regex=False)
        else:
            # otherwise report by committee and rule
            ylabel = "Committee/Rule"
            df["label"] = (
                df[["committee", "rule"]]
                .astype(str)
                .apply(
                    lambda x: f"{x.committee.str.replace(' ', '0', regex=False)}/{x.rule.str.replace(' ', '0', regex=False)}",
                    axis=1,
                )
            )

        return df, ylabel
