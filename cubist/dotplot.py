from warnings import warn
import math

try:
    from sklearn.utils._optional_dependencies import check_matplotlib_support
except Exception:
    from sklearn.utils import check_matplotlib_support

import pandas as pd

# from .cubist import Cubist


class DotplotDisplay:
    def __init__(self) -> None:
        pass

    def plot(self, df: pd.DataFrame, ax):
        check_matplotlib_support(f"{self.__class__.__name__}.plot")
        import matplotlib.pyplot as plt

        if ax is None:
            fig = plt.figure()
            n_subplots_xy = math.sqrt(df.variable.nunique())
            gs = fig.add_gridspec(
                math.ceil(n_subplots_xy),
                math.floor(n_subplots_xy),
                hspace=0.3,
                wspace=0,
            )
            ax = gs.subplots(sharex="all", sharey="all")
            ax = ax.reshape(-1)

    @classmethod
    def from_estimator(
        cls,
        estimator,
        what: str = "splits",
        committee: int = None,
        rule: int = None,
        ax=None,
        scatter_kwargs=None,
        line_kwargs=None,
    ):
        check_matplotlib_support(f"{cls.__class__.__name__}.from_estimator")

        expected_what = ("splits", "coeffs")
        if what not in expected_what:
            raise ValueError(
                f"`what` must be one of {', '.join(expected_what)}. "
                f"Got {what!r} instead."
            )

        import matplotlib.pyplot as plt

        if what == "splits":
            df = estimator.splits_.copy()
            if (df.type == "categorical").all():
                warn("No splits of continuous predictors were made")
                return
            df = df.loc[df.type == "continuous"].reset_index(drop=True)
        else:
            df = estimator.coeffs_.copy()
            df = pd.melt(df, id_vars=["committee", "rule"])
            df = df.loc[df.notna().all(axis="columns")]

        if df.empty:
            warn(f"No {what} were used in this model")
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
            lab = "Rule"
            df["label"] = df.rule.astype(str).str.replace(" ", "0", regex=False)
        else:
            lab = "Committee/Rule"
            df["label"] = (
                df[["committee", "rule"]]
                .astype(str)
                .apply(
                    lambda x: f"{x.committee.str.replace(' ', '0', regex=False)}/{x.rule.str.replace(' ', '0', regex=False)}",
                    axis=1,
                )
            )

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
            fig = plt.gcf()

        if what == "splits":
            for i, var in enumerate(list(df.variable.unique())):
                # add trellis lines
                for label in sorted(list(df.label.unique())):
                    ax[i].plot([0, 1], [label, label], color="#e9e9e9")
                    ax[i].set_xlim([-0.05, 1.05])
                # plot data
                for _, row in df.loc[df.variable == var].iterrows():
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
            fig.supylabel(lab)
            fig.suptitle(f"Training Data Coverage by {lab} and Variable")

        else:
            for i, var in enumerate(list(df.variable.unique())):
                ax[i].scatter("value", "label", data=df.loc[df.variable == var])
                ax[i].set_title(var)

            for j in range(i + 1, ax.shape[0]):
                ax[j].set_axis_off()

            fig.supxlabel("Coefficient Value")
            fig.supylabel(lab)
            fig.suptitle(f"Model Coefficients by {lab} and Variable")

        return ax
