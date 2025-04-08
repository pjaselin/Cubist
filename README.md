# Cubist

[![PyPI Version](https://badge.fury.io/py/cubist.svg)](https://badge.fury.io/py/cubist)
[![GitHub Build](https://github.com/pjaselin/Cubist/actions/workflows/tests.yml/badge.svg)](https://github.com/pjaselin/Cubist/actions)
[![codecov](https://codecov.io/gh/pjaselin/Cubist/graph/badge.svg?token=8FAZDANIP7)](https://codecov.io/gh/pjaselin/Cubist)
[![License](https://img.shields.io/pypi/l/cubist.svg)](https://pypi.python.org/pypi/cubist)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cubist.svg)](https://pypi.org/project/cubist)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/cubist)](https://pypi.org/project/cubist)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

`cubist` is a Python package and wrapper for [Ross Quinlan](https://www.rulequest.com/Personal/)'s [Cubist](https://www.rulequest.com/cubist-unix.html) v2.07 regression model with additional utilities for visualizing the model. The package is both inspired by and a translation of the [R wrapper for Cubist](https://github.com/topepo/Cubist). This implementation of the model is compatible with and the visualization utilities are designed after those in [scikit-learn](https://scikit-learn.org/stable/).

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Installation](#installation)
  - [Model-Only](#model-only)
  - [Enable Visualization Utilities](#enable-visualization-utilities)
- [Usage](#usage)
- [Cubist Model Features](#cubist-model-features)
- [Package Features](#package-features)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installation

### Model-Only

```bash
pip install --upgrade cubist
```

### Enable Visualization Utilities

```bash
pip install cubist[viz]
```

## Usage

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

## Cubist Model Features

The Cubist model has the following distinguishing features, although not all are fully enabled in this package:

- Generates a piecewise model formulated as a collection of conditional rules with corresponding linear regressors (optionally allowing for nearest-neighbor correction).
- High interpretability due to piecewise rules and linear regressors.
- Handles missing values.
- Handles continuous, date, time, timestamp, and discrete values. Additionally can ignore columns and add labels to training rows. Columns can also be defined by formulas. N.B. Not all of these are supported in this package.
- Natively performs cross-validation and sampling.
- Error can be further reduced by using multiple models (committees).
- Allows for extrapolation beyond the original training target values (sets a minimum of zero for predicted output if all training target values are greater than zero).

## Package Features

- Cubist model exposed as a scikit-learn estimator.
- Visualization utilities for:
  - Exploring the coefficients of the linear regressors.
  - Assessing the coverage of rules over an input dataset.
