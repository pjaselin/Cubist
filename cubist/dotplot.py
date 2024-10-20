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

    # if ax is None:
    #     fig = plt.figure()
    #     gs = fig.add_gridspec(3, hspace=0)
    #     ax = gs.subplots(sharex=True, sharey=True)

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
            splits = splits[splits.committee <= committee]

        if rule is not None:
            if not isinstance(rule, int):
                raise TypeError(f"`rule` must be an integer but got {type(rule)}")
            splits = splits[splits.rule <= rule]

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
                math.ceil(n_subplots_xy), math.floor(n_subplots_xy), hspace=0, wspace=0
            )
            ax = gs.subplots(sharex="col", sharey="row")
            ax = ax.reshape(-1)
        fig.suptitle(f"Sharing x per column, y per row {lab}")
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
            ax = gs.subplots(sharex="col", sharey="row")
            ax = ax.reshape(-1)

        for i, var in enumerate(list(coeffs.variable.unique())):
            ax[i].scatter("value", "label", data=coeffs[coeffs.variable == var])
            ax[i].set_title(var)

        fig.supxlabel("Coefficient Value")
        fig.supylabel(lab)
        fig.suptitle(f"Model Coefficients by {lab} and Variable")
        # TODO: make the x and y axis ticks match range and number of ticks/splits
        print(coeffs)

    return ax
