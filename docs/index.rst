.. cubist documentation master file, created by
   sphinx-quickstart on Sun Jan  5 14:13:50 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cubist Documentation
====================

``cubist`` is a Python package and wrapper for Ross Quinlan's `Cubist <https://www.rulequest.com/cubist-unix.html>`_ v2.07 regression model with additional utilities for visualizing the model. It is inspired by and based on the `R wrapper <https://github.com/topepo/Cubist>`_ for Cubist. The model is compatible with `scikit-learn <https://scikit-learn.org/stable/>`_ and the visualization utilities are designed after the same package.


==========
Background
==========

Cubist is a regression algorithm developed by Ross Quinlan for generating rule-based predictive models. Unlike other ensemble models such as `RandomForest <https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html>`_ and `XGBoost <https://xgboost.readthedocs.io/en/stable/>`_, Cubist generates a set of rules, making it easy to understand precisely how the model makes it's predictive decisions. Tools such as `SHAP <https://shap.readthedocs.io/en/latest/>`_ and `lime <https://github.com/marcotcr/lime>`_ are therefore unnecessary as Cubist doesn't exhibit black box behavior.

Like XGBoost, Cubist can perform boosting by the addition of more models (called committees) that correct for the error of prior models (i.e. the second model created corrects for the prediction error of the first, the third for the error of the second, etc.).

In addition to boosting, the model can perform instance-based (nearest-neighbor) corrections to create composite models, combining the advantages of these two methods. Note that with instance-based correction, model accuracy may be improved at the expense of compute time (this extra step takes longer) and some interpretability as the linear regression rules are no longer completely followed. It should also be noted that the disk size of a saved composite model will be proportional to the training dataset as the latter will be stored in the model to enable inferencing with instance-based corrections. A composite model will be used when `auto=False` with `neighbors` set to an integer between 1 and 9. Cubist can be allowed to decide whether to take advantage of composite models with `auto=True` and `neighbors` left unset.

========
Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started/installation

.. toctree::
   :maxdepth: 2
   :caption: Usage

   usage/cubist
   usage/visualizations

.. toctree::
   :maxdepth: 2
   :caption: API Docs

   api/cubist
   api/cubist_coefficient_display
   api/cubist_coverage_display
   api/exceptions

================
Acknowledgements
================
Cubist is a regression algorithm developed by Ross Quinlan for generating rule-based predictive models. This has been available in the R world thanks to the work of Max Kuhn and his colleagues. It is introduced to Python with this package and made scikit-learn compatible for use with at ecosystem. Cross-validation and control over whether Cubist creates a composite model is also enabled here.
Grateful to Kirk Mettler for introducing me to the model
Quinlan for his work on the model
Max Kuhn for developing the R package on which this is based
