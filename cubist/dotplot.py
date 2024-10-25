from warnings import warn
import math

try:
    from sklearn.utils._optional_dependencies import check_matplotlib_support
except Exception:
    from sklearn.utils import check_matplotlib_support

import pandas as pd

from .cubist import Cubist


class DotplotDisplay:
    def __init__(self) -> None:
        pass

    def plot(self):
        check_matplotlib_support(f"{self.__class__.__name__}.plot")
        # import matplotlib.pyplot as plt

        pass

    @classmethod
    def from_estimator(
        cls,
        estimator,
        X,
        y,
        what: str = "splits",
        committee: int = None,
        rule: int = None,
        ax=None,
        scatter_kwargs=None,
        line_kwargs=None,
    ):
        check_matplotlib_support(f"{cls.__class__.__name__}.from_estimator")

        y_pred = estimator.predict(X)

        return cls.from_predictions(
            y_true=y,
            y_pred=y_pred,
            what=what,
            committee=committee,
            rule=rule,
            ax=ax,
            scatter_kwargs=scatter_kwargs,
            line_kwargs=line_kwargs,
        )

    @classmethod
    def from_predictions(
        cls,
        y_true,
        y_pred,
        *,
        what: str = "splits",
        committee: int = None,
        rule: int = None,
        ax=None,
        scatter_kwargs=None,
        line_kwargs=None,
    ):
        check_matplotlib_support(f"{cls.__class__.__name__}.from_predictions")
        pass


def dotplot(
    model: Cubist,
    what: str = "splits",
    committee: int = None,
    rule: int = None,
    ax=None,
):
    """Create lattice dotplots of the rule conditions or the linear model
    coefficients produced by Cubist.

    Parameters
    ----------
    model : Cubist
        The training input samples. Must have complete column names or none
        provided at all (NumPy arrays will be given names by column index).

    what : str, default="splits"
        "splits" or "coeffs" Optional vector of sample weights that is the same length as y for
        how much each instance should contribute to the model fit.

    committee : int, default=None

    rule : int, default=None

    ax : matplotlib axes, default=None
        Axes object to plot on. If `None`, a new figure and axes is created.

    Returns
    -------
    self : object
    """
    # check_matplotlib_support(f"{self.__class__.__name__}.plot")

    import matplotlib.pyplot as plt

    expected_what = ("splits", "coeffs")
    if what not in expected_what:
        raise ValueError(
            f"`what` must be one of {', '.join(expected_what)}. "
            f"Got {what!r} instead."
        )

    if what == "splits":
        splits = model.splits_.copy()
        if splits.empty:
            # showing a message and stop here
            warn("No splits were used in this model")
            return

        if committee is not None:
            if not isinstance(committee, int):
                raise TypeError(
                    f"`committee` must be an integer but got {type(committee)}"
                )
            splits = splits.loc[splits.committee <= committee]

        if rule is not None:
            if not isinstance(rule, int):
                raise TypeError(f"`rule` must be an integer but got {type(rule)}")
            splits = splits.loc[splits.rule <= rule]

        if splits.committee.max() == 1:
            lab = "Rule"
            splits["label"] = splits.rule.apply(lambda x: str(x).replace(" ", "0"))
        else:
            lab = "Committee/Rule"
            splits["label"] = splits.apply(
                lambda x: f"{x.committee.replace(' ', '0')}/{x.rule.replace(' ', '0')}",
                axis=1,
            )

        if (splits.type == "categorical").all():
            warn("No splits of continuous predictors were made")
            return

        # TODO consume the optionally provided ax but use below code
        if ax is None:
            fig = plt.figure()
            n_subplots_xy = math.sqrt(splits.variable.nunique())
            gs = fig.add_gridspec(
                math.ceil(n_subplots_xy),
                math.floor(n_subplots_xy),
                hspace=0.3,
                wspace=0,
            )
            ax = gs.subplots(sharex="all", sharey="all")
            ax = ax.reshape(-1)

        splits = splits.loc[splits.type == "continuous"].reset_index(drop=True)

        for i, var in enumerate(list(splits.variable.unique())):
            # add trellis lines
            for label in sorted(list(splits.label.unique())):
                ax[i].plot([0, 1], [label, label], color="#e9e9e9")
                # ax[i].set_title(var)
                ax[i].set_xlim([-0.05, 1.05])
            # plot data
            for _, row in splits.loc[splits.variable == var].iterrows():
                if "<" in row["dir"]:
                    x = [0, row["percentile"]]
                    color = "#1E88E5"
                else:
                    x = [row["percentile"], 1]
                    color = "#ff0d57"
                ax[i].plot(x, [row["label"], row["label"]], color=color)
                ax[i].set_title(var)
                # ax[i].set_xlim([-0.05, 1.05])

        fig.supxlabel("Training Data Coverage")
        fig.supylabel(lab)
        fig.suptitle(f"Training Data Coverage by {lab} and Variable")
    else:
        coeffs = model.coeff_.copy()
        if coeffs.empty:
            # showing a message and stop here
            warn("No coefficients were used in this model")
            return

        coeffs = pd.melt(coeffs, id_vars=["committee", "rule"])
        coeffs = coeffs.loc[coeffs.notna().all(axis="columns")]

        if coeffs.committee.max() == 1:
            lab = "Rule"
            coeffs["label"] = coeffs.rule.apply(lambda x: str(x).replace(" ", "0"))
        else:
            lab = "Committee/Rule"
            coeffs["label"] = coeffs.apply(
                lambda x: f"{x.committee.replace(' ', '0')}/{x.rule.replace(' ', '0')}",
                axis=1,
            )
        if ax is None:
            fig = plt.figure()
            n_subplots_xy = math.sqrt(coeffs.variable.nunique())
            gs = fig.add_gridspec(
                math.ceil(n_subplots_xy),
                math.floor(n_subplots_xy),
                hspace=0.3,
                wspace=0,
            )
            ax = gs.subplots(sharex="all", sharey="all")
            ax = ax.reshape(-1)

        for i, var in enumerate(list(coeffs.variable.unique())):
            ax[i].scatter("value", "label", data=coeffs.loc[coeffs.variable == var])
            ax[i].set_title(var)

        fig.supxlabel("Coefficient Value")
        fig.supylabel(lab)
        fig.suptitle(f"Model Coefficients by {lab} and Variable")

    return ax
