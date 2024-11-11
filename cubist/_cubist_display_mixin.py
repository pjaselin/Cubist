import math

import pandas as pd

try:
    from sklearn.utils._optional_dependencies import check_matplotlib_support
except Exception:
    from sklearn.utils import check_matplotlib_support


class CubistDisplayMixin:
    def _make_fig(self, *, ax=None, df: pd.DataFrame = None):
        check_matplotlib_support(f"{self.__class__.__name__}.plot")
        import matplotlib.pyplot as plt

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
                gridspec_kw=dict(hspace=0.5, wspace=0),
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

        df = df.loc[df.type == "continuous"].reset_index(drop=True)

        if df.empty:
            raise ValueError(
                "No splits of continuous predictors were used in this model"
            )

        if committee is not None:
            if not isinstance(committee, int):
                raise TypeError(
                    f"`committee` must be an integer but got {type(committee)}"
                )
            df = df.loc[df.committee <= committee]

        if rule is not None:
            if not isinstance(rule, int):
                raise TypeError(f"`rule` must be an integer but got {type(rule)}")
            df = df.loc[df.rule <= rule]

        if df.committee.max() == 1:
            ylabel = "Rule"
            df["label"] = df.rule.astype(str).str.replace(" ", "0", regex=False)
        else:
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
