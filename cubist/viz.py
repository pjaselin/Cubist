from warnings import warn
import math

try:
    from sklearn.utils._optional_dependencies import check_matplotlib_support
except Exception:
    from sklearn.utils import check_matplotlib_support


from .cubist import Cubist


class DotplotDisplay:
    def __init__(self) -> None:
        pass

    def plot(self):
        check_matplotlib_support(f"{self.__class__.__name__}.plot")
        # import matplotlib.pyplot as plt

        pass

    @classmethod
    def from_estimator(cls):
        pass

    @classmethod
    def from_predictions(cls):
        pass


def dotplot(
    model: Cubist,
    data=None,
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

    data : {array-like} of shape (n_samples, n_features)
        The target values (Real numbers in regression).

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

    splits = model.splits_.copy()
    if splits.empty:
        # showing a message and stop here
        warn("No splits were used in this model")
        return

    expected_what = ("splits", "coeffs")
    if what not in expected_what:
        raise ValueError(
            f"`what` must be one of {', '.join(expected_what)}. "
            f"Got {what!r} instead."
        )

    if committee is not None:
        if not isinstance(committee, int):
            raise TypeError(f"`committee` must be an integer but got {type(committee)}")
        splits = splits[splits.committee <= committee]

    if rule is not None:
        if not isinstance(rule, int):
            raise TypeError(f"`rule` must be an integer but got {type(rule)}")
        splits = splits[splits.rule <= rule]

    if splits.committee.max() == 1:
        lab = "Rule"
        splits["label"] = splits.rule.apply(lambda x: x.replace(" ", "0"))
    else:
        lab = "Committee/Rule"
        splits["label"] = splits.apply(
            lambda x: f"{x.committee.replace(' ', '0')}/{x.rule.replace(' ', '0')}",
            axis=1,
        )

    if ax is None:
        _, ax = plt.subplots()

    if what == "splits":
        if (splits.type == "categorical").all():
            warn("No splits of continuous predictors were made")
            return

        n_subplots_xy = math.sqrt(splits.variable.nunique())
        # subplot_xy = itertools.product(
        #     range(math.ceil(n_subplots_xy)), range(math.floor(n_subplots_xy))
        # )

        # TODO consume the optionally provided ax but use below code
        fig = plt.figure()
        gs = fig.add_gridspec(
            math.ceil(n_subplots_xy), math.floor(n_subplots_xy), hspace=0, wspace=0
        )
        axs = gs.subplots(sharex="col", sharey="row")
        fig.suptitle(f"Sharing x per column, y per row {lab}")

    return axs
