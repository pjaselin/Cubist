.. cubist documentation master file, created by
   sphinx-quickstart on Sun Jan  5 14:13:50 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cubist Documentation
====================

``cubist`` is a Python package and wrapper for `Ross Quinlan <https://www.rulequest.com/Personal/>`_'s `Cubist <https://www.rulequest.com/cubist-unix.html>`_ v2.07 regression model with additional utilities for visualizing the model. The package is both inspired by and a translation of the `R wrapper for Cubist <https://github.com/topepo/Cubist>`_. This implementation of the model is compatible with and the visualization utilities are designed after `scikit-learn <https://scikit-learn.org/stable/>`_.

TL;DR
-----

.. code-block:: shell

   pip install cubist

.. doctest::

    >>> from sklearn.datasets import load_iris
    >>> from sklearn.model_selection import train_test_split
    >>> from cubist import Cubist
    >>> X, y = load_iris(return_X_y=True, as_frame=True)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y,
    ...                                                     random_state=42,
    ...                                                     test_size=0.05)
    >>> model = Cubist(n_rules=2, verbose=True)
    >>> model.fit(X_train, y_train)  # doctest: +NORMALIZE_WHITESPACE
    <BLANKLINE>
    Cubist [Release 2.07 GPL Edition]  ...
    ---------------------------------
    <BLANKLINE>
        Target attribute `outcome'
    <BLANKLINE>
    Read 142 cases (5 attributes)
    <BLANKLINE>
    Model:
    <BLANKLINE>
      Rule 1: [48 cases, mean 0.0, range 0 to 0, est err 0.0]
    <BLANKLINE>
        if
            petal width (cm) <= 0.6
        then
            outcome = 0
    <BLANKLINE>
      Rule 2: [94 cases, mean 1.5, range 1 to 2, est err 0.2]
    <BLANKLINE>
        if
            petal width (cm) > 0.6
        then
            outcome = 0.2 + 0.76 petal width (cm) + 0.271 petal length (cm)
                    - 0.45 sepal width (cm)
    <BLANKLINE>
    <BLANKLINE>
    Evaluation on training data (142 cases):
    <BLANKLINE>
        Average  |error|                0.1
        Relative |error|               0.16
        Correlation coefficient        0.98
    <BLANKLINE>
    <BLANKLINE>
            Attribute usage:
              Conds  Model
    <BLANKLINE>
              100%    66%    petal width (cm)
                      66%    sepal width (cm)
                      66%    petal length (cm)
    <BLANKLINE>
    <BLANKLINE>
    Time: 0.0 secs
    <BLANKLINE>
    Cubist(n_rules=2, verbose=True)


Background
----------

Cubist is a regression algorithm developed by Ross Quinlan for generating rule-based predictive models. This has been available in the R world thanks to the work of Max Kuhn and his colleagues. With this package, Cubist is introduced to Python and made scikit-learn compatible. Cross-validation and control over whether Cubist creates a composite model is also enabled here. Unlike other ensemble models such as `RandomForest <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html>`_ and `XGBoost <https://xgboost.readthedocs.io/en/stable/>`_, a Cubist model is comprised of a set of rules containing pairs of conditions and corresponding linear regression models, covering the full domain of the training dataset. Each rule is formulated as:

::

    if
        [conditions]
    then
        [linear model]

This makes it straightforward to understand how the model makes it's predictive decisions. Tools such as `SHAP <https://shap.readthedocs.io/en/latest/>`_ and `lime <https://github.com/marcotcr/lime>`_ are therefore unnecessary as Cubist doesn't exhibit black box behavior. A full example model:

.. dropdown:: Sample Cubist Output

   ::

      Cubist [Release 2.07 GPL Edition]  Sat Dec 28 19:52:49 2024
      ---------------------------------

          Target attribute `outcome'

      Read 142 cases (5 attributes)

      Model:

        Rule 1: [48 cases, mean 0.0, range 0 to 0, est err 0.0]

          if
              petal width (cm) <= 0.6
          then
              outcome = 0

        Rule 2: [94 cases, mean 1.5, range 1 to 2, est err 0.2]

          if
              petal width (cm) > 0.6
          then
              outcome = 0.2 + 0.76 petal width (cm) + 0.271 petal length (cm)
                        - 0.45 sepal width (cm)


      Evaluation on training data (142 cases):

          Average  |error|                0.1
          Relative |error|               0.16
          Correlation coefficient        0.98


              Attribute usage:
                Conds  Model

                100%    66%    petal width (cm)
                        66%    sepal width (cm)
                        66%    petal length (cm)


      Time: 0.0 secs

In the above sample using the `Iris dataset <https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html>`_, the Cubist model contains two rules where the outcome (y-value) is 0 when `petal width (cm)` <= 0.6 and otherwise the outcome is given by 0.2 + 0.76 `petal width (cm)` + 0.271 `petal length (cm)` - 0.45 `sepal width (cm)`.

Like XGBoost, Cubist can perform boosting by the addition of more models (called committees) that correct for the error of prior models (i.e. the second model created corrects for the prediction error of the first, the third for the error of the second, etc.).

In addition to boosting, the model supports instance-based (nearest-neighbor) corrections to create composite models, combining the advantages of these two methods. Note that with instance-based correction, model accuracy may be improved at the expense of compute time as this extra step takes longer and somewhat reduced interpretability as the linear models are no longer completely followed. It should also be noted that the disk size of a saved composite model will be proportional to the training dataset size as the latter will be stored with the model to enable future inferencing with instance-based corrections. Interestingly, Cubist can be allowed to decide whether to take advantage of composite models with the appropriate settings and will report it's choice to the user.

A final difference with other models is that Cubist natively supports missing and categorical values. This means user are not required to introduce encodings if not desired and may exlore more patterns (e.g. missingness) in the dataset.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started/installation

.. toctree::
   :maxdepth: 2
   :caption: Usage

   usage/model
   usage/visualizations

.. toctree::
   :maxdepth: 2
   :caption: API Docs

   api/model
   api/visualizations
   api/exceptions

Considerations
--------------

- For small datasets, using the `sample` parameter is probably inadvisable as Cubist won't have enough samples to produce a representative model.
- If you are looking for fast inferencing and can spare accuracy, consider skipping using a composite model by leaving `neighbors` unset.
- Models that produce one or more rules without splits (i.e. a single linear model which holds true for the entire dataset), will return an empty `splits_`attribute while the coefficients will be available in the `coeffs_` attribute.

Benchmarks
----------

There are many literature examples demonstrating the power of Cubist and comparing it to Random Forest as well as other bootstrapped/boosted models. Some of these are compiled here: [Cubist in Use](https://www.rulequest.com/cubist-pubs.html). To demonstrate this, some benchmark scripts are provided in the respectively named folder.

Literature
----------

Original Paper
^^^^^^^^^^^^^^

- `Learning with Continuous Classes <https://sci2s.ugr.es/keel/pdf/algorithm/congreso/1992-Quinlan-AI.pdf)>`_

Publications Using Cubist
^^^^^^^^^^^^^^^^^^^^^^^^^

- `Cubist in Use <https://www.rulequest.com/cubist-pubs.html>`_
- `A Machine Learning Example in R using Cubist <https://www.linkedin.com/pulse/machine-learning-example-r-using-cubist-kirk-mettler>`_

Acknowledgements
----------------

While the positive feedback for this package is appreciated, all credit rightly belongs to `Ross Quinlan <https://www.rulequest.com/Personal/>`_ for his work in developing the Cubist model and it's related classification algorithms such as C5.0. He also provides a commercial edition for those looking to leverage Cubist more fully.

I also want to give credit to `Max Kuhn <https://github.com/topepo>`_ and his colleagues for developing the R wrapper for Cubist. This package is more or less a Python translation of that effort so the heavylifting in understanding how to control the Cubist C library came from them. Without that project, there would have been no inspiration or blueprint for this one.

Finally, I want to express my gratitude to `Kirk Mettler <https://www.linkedin.com/in/kirkmettler/>`_, my former mentor at IBM, for introducing me to this model and encouraging me to embark on this effort.

Besides the value of this work, this project has also served as a practical means of learning over the past few years:

Beyond the value to end users in this effort, this project has been useful in:

- Learning Python packaging
- Shoring up understanding of pytest/coverage, CI/CD with GitHub Actions
- Learning Sphinx, restructured Markdown, pre-commit, mypy

- Python packaging (cibuildwheel)
- CI/CD via GitHub Actions
- pytest
- coverage/CodeCov
- pre-commit
- sphinx
- cython
- ruff
- pylint
