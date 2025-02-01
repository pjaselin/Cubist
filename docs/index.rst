.. cubist documentation master file, created by
   sphinx-quickstart on Sun Jan  5 14:13:50 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cubist Documentation
====================

``cubist`` is a Python package and wrapper for Ross Quinlan's `Cubist <https://www.rulequest.com/cubist-unix.html>`_ v2.07 regression model with additional utilities for visualizing the model. It is both inspired by and a translation of the `R wrapper <https://github.com/topepo/Cubist>`_ for Cubist. The model is compatible with and the visualization utilities are designed after `scikit-learn <https://scikit-learn.org/stable/>`_.

Background
----------

Cubist is a regression algorithm developed by Ross Quinlan for generating rule-based predictive models. Unlike other ensemble models such as `RandomForest <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html>`_ and `XGBoost <https://xgboost.readthedocs.io/en/stable/>`_, a Cubist model is comprised of a set of rules containing pairs of conditions and corresponding multivariate linear regression models, covering the full domain of the training dataset. Each rule is formulated as:

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

In addition to boosting, the model supports instance-based (nearest-neighbor) corrections to create composite models, combining the advantages of these two methods. Note that with instance-based correction, model accuracy may be improved at the expense of compute time as this extra step takes longer and somewhat reduced interpretability as the multivariate linear models are no longer completely followed. It should also be noted that the disk size of a saved composite model will be proportional to the training dataset size as the latter will be stored with the model to enable future inferencing with instance-based corrections. Interestingly, Cubist can be allowed to decide whether to take advantage of composite models with the appropriate settings and will report it's choice to the user.

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

Acknowledgements
----------------

While I appreciate the positive responses from this effort, I'm truly only a messenger. All credit is due to Ross Quinlan for his work in developing Cubist and it's related classification algorithms such as C5.0. If not for Max Kuhn and his colleagues, I wouldn't have known where to start. This project is more or less a Python translation of Max's R package so the heavylifting in understanding how to control the Cubist C library came from them.

Finally I'm also grateful to my leadership at IBM, Kirk Mettler, for introducing me to Cubist and from whom I first conceived of this effort.
 the R world thanks to the work of Max Kuhn and his colleagues. It is introduced to Python with this package and made scikit-learn compatible for use with at ecosystem. Cross-validation and control over whether Cubist creates a composite model is also enabled here.

Grateful to Kirk Mettler for introducing me to the model
Quinlan for his work on the model
Max Kuhn for developing the R package on which this is based

Besides the value of this work, this project has also served as a practical means of learning over the past few years:

- Python packaging (cibuildwheel)
- CI/CD via GitHub Actions
- pytest
- coverage/CodeCov
- pre-commit
- sphinx
- cython
- ruff
- pylint
