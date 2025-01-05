"""Base class for Cubist plotting utilities"""

import math

import pandas as pd
import numpy as np

from sklearn.utils._optional_dependencies import check_matplotlib_support


class _CubistDisplayMixin:  # pylint: disable=R0903
    """Mixin class to be used in Displays for Cubist.

    The aim of this class is to centralize some validations for generating the
    matplotlib figure and axes as well as for processing the data to be plotted.
    """

    def _validate_plot_params(
        self, *, ax=None, df: pd.DataFrame = None, gridspec_kwargs: dict = None
    ):
        check_matplotlib_support(f"{self.__class__.__name__}.plot")
        import matplotlib.pyplot as plt  # pylint: disable=C0415

        if gridspec_kwargs is None:
            gridspec_kwargs = {}

        if ax is None:
            # number of plots to be created
            nplots = df.variable.nunique()
            # get the number of columns and rows required to create this many
            # plots as a square-ish grid
            nrows = ncols = int(round(math.sqrt(nplots)))
            # if the square root of the number of plots rounds down
            # then add 1 to the number of rows
            if nplots > (nrows * ncols):
                nrows += 1
            # create subplots with ncols/nrows, sharing the x and y axes, and
            # merging in gridspec configurations
            fig, ax = plt.subplots(
                ncols=ncols,
                nrows=nrows,
                sharex="all",
                sharey="all",
                gridspec_kw={"hspace": 0.5, "wspace": 0} | gridspec_kwargs,
            )

            # ax is a numpy array and so we reshape it to one dimension for
            # simpler processing
            if isinstance(ax, np.ndarray):
                ax = ax.reshape(-1)
            # if there is only one plot created, place it in a numpy array
            else:
                ax = np.array([ax])
        # if ax is provided, get the current figure
        else:
            fig = plt.gcf()
        return fig, ax

    @classmethod
    def _validate_from_estimator_params(
        cls,
        *,
        df: pd.DataFrame = None,
        committee: int = None,
        rule: int = None,
        feature_names: list = None,
    ):
        check_matplotlib_support(f"{cls.__name__}.from_estimator")

        # make sure dataframe is sorted by committee and rule
        df = df.sort_values(by=["committee", "rule"]).reset_index(drop=True)

        # if the committee parameter is passed
        if committee is not None:
            # verify committee parameter is integer
            if not isinstance(committee, int):
                raise TypeError(
                    f"`committee` must be an integer but got {type(committee)}."
                )
            # filter for committees below requested committee number
            df = df.loc[df.committee <= committee]

        # if rule parameter is passed
        if rule is not None:
            # verify rule parameter is integer
            if not isinstance(rule, int):
                raise TypeError(f"`rule` must be an integer but got {type(rule)}.")
            # filter for rules below requested rule number
            df = df.loc[df.rule <= rule]

        # if feature_names parameter is passed
        if feature_names is not None:
            # verify feature_names is a list
            if not isinstance(feature_names, list):
                raise TypeError(f"`feature_names` must be a list but got {type(rule)}.")
            # filter for rows where the attribute/variable name is found in
            # the list
            df = df.loc[df.variable.isin(feature_names)]
            # verify the dataframe is not empty now
            if df.empty:
                raise ValueError(
                    f"No rows are available given `feature_names`: {feature_names}."
                )

        # reset the index since this is used for labelling
        df = df.reset_index(drop=True)

        # create the y-axis labels and y-tick values
        if df.committee.max() == 1:
            # if there is only one committee, this is a rule-only model
            y_axis_label = "Rule"
            df["label"] = df.rule
        else:
            # otherwise report by committee and rule
            y_axis_label = "Committee/Rule"
            # create label column for committee/rule pair
            df["label"] = df[["committee", "rule"]].apply(
                lambda x: f"{x.committee}/{x.rule}",
                axis=1,
            )
        # get the distinct ordered labels
        y_label_map = df.label.drop_duplicates().reset_index(drop=True).to_dict()
        # get the labels as a list
        y_labels = list(y_label_map.values())
        # replace the dataframe label column values with the index of the
        # same value in y_labels
        df.label = df.label.apply(y_labels.index)
        return df, y_axis_label, y_label_map
