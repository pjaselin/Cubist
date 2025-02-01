# Cubist

[![PyPI Version](https://badge.fury.io/py/cubist.svg)](https://badge.fury.io/py/cubist)
[![GitHub Build](https://github.com/pjaselin/Cubist/actions/workflows/tests.yml/badge.svg)](https://github.com/pjaselin/Cubist/actions)
[![codecov](https://codecov.io/gh/pjaselin/Cubist/graph/badge.svg?token=8FAZDANIP7)](https://codecov.io/gh/pjaselin/Cubist)
[![License](https://img.shields.io/pypi/l/cubist.svg)](https://pypi.python.org/pypi/cubist)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cubist.svg)](https://pypi.org/project/cubist)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/cubist)](https://pypi.org/project/cubist)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A Python package and wrapper for Ross Quinlan's [Cubist](https://www.rulequest.com/cubist-unix.html) v2.07 regression model. Both inspired by and a translation of the [R wrapper](https://github.com/topepo/Cubist) for Cubist. The model is compatible with and the visualization utilities are designed after [scikit-learn](https://scikit-learn.org/stable/).

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Installation](#installation)
  - [Model-Only](#model-only)
  - [Optional Dependencies](#optional-dependencies)
- [Background](#background)
- [Advantages](#advantages)
- [Sample Usage](#sample-usage)
- [Cubist Model Class](#cubist-model-class)
  - [Model Parameters](#model-parameters)
  - [Model Attributes](#model-attributes)
- [Visualization Utilities](#visualization-utilities)
  - [Coefficient Display](#coefficient-display)
  - [Coverage Display](#coverage-display)
- [Considerations](#considerations)
- [Benchmarks](#benchmarks)
- [Literature for Cubist](#literature-for-cubist)
  - [Original Paper](#original-paper)
  - [Publications Using Cubist](#publications-using-cubist)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installation

### Model-Only

```bash
pip install --upgrade cubist
```

### Optional Dependencies

To enable visualization utilities:

```bash
pip install cubist[viz]
```

For development:

```bash
pip install cubist[dev,viz]
```

## Background

Cubist is a regression algorithm developed by Ross Quinlan for generating rule-based predictive models. This has been available in the R world thanks to the work of Max Kuhn and his colleagues and with this package is introduced to Python and made scikit-learn compatible. Cross-validation and control over whether Cubist creates a composite model is also enabled here.

## Advantages

Unlike other ensemble models such as [RandomForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html) and [XGBoost](https://xgboost.readthedocs.io/en/stable/), Cubist generates rules as a set of multivariate linear models with conditions (formulated as if [set of conditions met] then [multivariate linear model for given conditions]), making it easy to understand precisely how the model makes it's predictive decisions. Tools such as [SHAP](https://shap.readthedocs.io/en/latest/) and [lime](https://github.com/marcotcr/lime) are therefore unnecessary as Cubist doesn't exhibit black box behavior. See [Sample Usage](#sample-usage) for the printed model.

Like XGBoost, Cubist can perform boosting by the addition of more models (called committees) that correct for the error of prior models (i.e. the second model created corrects for the prediction error of the first, the third for the error of the second, etc.).

In addition to boosting, the model can perform instance-based (nearest-neighbor) corrections to create composite models, combining the advantages of these two methods. Note that with instance-based correction, model accuracy may be improved at the expense of compute time (this extra step takes longer) and some interpretability as the multivariate linear models are no longer completely followed. It should also be noted that a composite model might be quite large as the full training dataset must be stored in order to perform instance-based corrections for inferencing. A composite model will be used when `auto=False` with `neighbors` set to an integer between 1 and 9. Cubist can be allowed to decide whether to take advantage of composite models with `auto=True` and `neighbors` left unset.

missing values, categorical values can be used

## Sample Usage

```python
>>> from sklearn.datasets import load_iris
>>> from sklearn.model_selection import train_test_split
>>> from cubist import Cubist
>>> X, y = load_iris(return_X_y=True, as_frame=True)
>>> X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.05
    )
>>> X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.05
    )
>>> model.fit(X_train, y_train)

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

Cubist(n_rules=2, verbose=True)
>>> model.predict(X_test)
array([1.1257    , 0.        , 2.04999995, 1.25449991, 1.30480003,
       0.        , 0.94999999, 1.93509996])
>>> model.score(X_test, y_test)
0.9543285583162371
```

## Cubist Model Class

### Model Parameters

The following parameters can be passed as arguments to the ```Cubist()``` class instantiation:

### Model Attributes

The following attributes are exposed to understand the Cubist model results:

## Visualization Utilities

Based on the R Cubist package, a few visualization utilities are provided to allow some exploration of trained Cubist models. Differing from the original package, these are extended somewhat to allow configuration of the subplots as well as for selecting a subset of variables/attributes to plot.

### Coefficient Display

The `CubistCoefficientDisplay` plots the multivariate linear regression coefficients and intercepts selected by the Cubist model. One subplot is created for each variable/attribute with the rule number or committee/rule pair on the y-axis and the coefficient value plotted along the x-axis.

![Sample Cubist Coefficient Display for Iris dataset](./static/iris_coefficient_display.png)

### Coverage Display

The `CubistCoverageDisplay` is used to visualize the coverage of rule splits for a given dataset. One subplot is created per input variable/attribute/column with the rule number or comittee/rule pair plotted on the y-axis and the coverage ranges plotted along the x-axis, scaled to the percentage of the variable values.

![Sample Cubist Coverage Display for Iris dataset](./static/iris_coverage_display.png)

## Considerations

- For small datasets, using the `sample` parameter is probably inadvisable as Cubist won't have enough samples to produce a representative model.
- If you are looking for fast inferencing and can spare accuracy, consider skipping using a composite model by leaving `neighbors` unset.
- Models that produce one or more rules without splits (i.e. a single multivariate linear model which holds true for the entire dataset), will return an empty `splits_`attribute while the coefficients will be available in the `coeffs_` attribute.

## Benchmarks

There are many literature examples demonstrating the power of Cubist and comparing it to Random Forest as well as other bootstrapped/boosted models. Some of these are compiled here: [Cubist in Use](https://www.rulequest.com/cubist-pubs.html). To demonstrate this, some benchmark scripts are provided in the respectively named folder.

## Literature for Cubist

### Original Paper

- [Learning with Continuous Classes](https://sci2s.ugr.es/keel/pdf/algorithm/congreso/1992-Quinlan-AI.pdf)

### Publications Using Cubist

- [Cubist in Use](https://www.rulequest.com/cubist-pubs.html)
- [A Machine Learning Example in R using Cubist](https://www.linkedin.com/pulse/machine-learning-example-r-using-cubist-kirk-mettler)
