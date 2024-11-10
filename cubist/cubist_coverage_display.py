from warnings import warn
import math

try:
    from sklearn.utils._optional_dependencies import check_matplotlib_support
except Exception:
    from sklearn.utils import check_matplotlib_support

import pandas as pd

from .cubist import Cubist


class CubistCoverageDisplay:
    def __init__(self, *, splits: pd.DataFrame):
        self.splits = splits

    def plot(
        self,
        ax=None,
        *,
        ylabel: str = None,
        scatter_kwargs: dict = None,
        line_kwargs: dict = None,
    ):
        check_matplotlib_support(f"{self.__class__.__name__}.plot")
        import matplotlib.pyplot as plt

        if ax is None:
            nplots = self.splits.variable.nunique()
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
            fig = plt.gcf()

        for i, var in enumerate(list(self.splits.variable.unique())):
            # add trellis lines
            for label in sorted(list(self.splits.label.unique())):
                ax[i].plot([0, 1], [label, label], color="#e9e9e9")
                ax[i].set_xlim([-0.05, 1.05])
            # plot data
            for _, row in self.splits.loc[self.splits.variable == var].iterrows():
                if "<" in row["dir"]:
                    x = [0, row["percentile"]]
                    color = "#1E88E5"
                else:
                    x = [row["percentile"], 1]
                    color = "#ff0d57"
                ax[i].plot(x, [row["label"], row["label"]], color=color)
                ax[i].set_title(var)

        for j in range(i + 1, ax.shape[0]):
            ax[j].set_axis_off()

        fig.supxlabel("Training Data Coverage")
        fig.supylabel(ylabel)
        fig.suptitle(f"Training Data Coverage by {ylabel} and Variable")

        self.ax_ = ax
        self.figure_ = ax.figure

        return self

    @classmethod
    def from_estimator(
        cls,
        estimator: Cubist,
        # what: str = "splits",
        committee: int = None,
        rule: int = None,
        ax=None,
        scatter_kwargs=None,
        line_kwargs=None,
    ):
        check_matplotlib_support(f"{cls.__name__}.from_estimator")

        df = estimator.splits_.copy()
        if (df.type == "categorical").all():
            warn("No splits of continuous predictors were made")
            return
        df = df.loc[df.type == "continuous"].reset_index(drop=True)

        if df.empty:
            warn("No splits were used in this model")
            return

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

        viz = cls(splits=df)
        return viz.plot(
            ax=ax, ylabel=ylabel, scatter_kwargs=scatter_kwargs, line_kwargs=line_kwargs
        )

    def from_predictions(self):
        raise NotImplementedError
