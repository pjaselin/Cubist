Model
#####

The Cubist model class (``cubist.Cubist``) has eleven parameters and eleven attributes available. Their use is demonstrated below and the class is documented in the :ref:`API Docs<api/model:Cubist>`.

A simple use of Cubist with no added configuration is as follows:

.. doctest::

    >>> from sklearn.datasets import load_iris
    >>> from sklearn.model_selection import train_test_split
    >>> from cubist import Cubist
    >>> X, y = load_iris(return_X_y=True, as_frame=True)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y,
    ...                                                     random_state=42,
    ...                                                     test_size=0.05)
    >>> model = Cubist()
    >>> model.fit(X_train, y_train)
    Cubist()
    >>> model.score(X_train, y_train)
    0.9656775005204449
    >>> model.score(X_test, y_test)
    0.9955073453292975

Parameters
**********

These are the values passed to the model at initialization.

Display Options
===============

These parameters configure and enable printing Cubist's model report.

target_label
------------

The printed result includes a name for the target/output (y) value. The ``target_label`` parameter can be changed to something other than the default of `outcome`.

verbose
-------

The ``verbose`` parameter indicates whether Cubist should print the generated model, summary, and training performance to the console. Either an integer or Python boolean is accepted.

.. dropdown:: Sample Verbose Output with Custom Target Label

    .. doctest::

        >>> from sklearn.datasets import load_iris
        >>> from sklearn.model_selection import train_test_split
        >>> from cubist import Cubist
        >>> X, y = load_iris(return_X_y=True, as_frame=True)
        >>> X_train, X_test, y_train, y_test = train_test_split(X, y,
        ...                                                     random_state=42,
        ...                                                     test_size=0.05)
        >>> model = Cubist(n_rules=2, verbose=True,
        ...                target_label="custom_output")
        >>> model.fit(X_train, y_train)  # doctest: +NORMALIZE_WHITESPACE
        <BLANKLINE>
        Cubist [Release 2.07 GPL Edition]  ...
        ---------------------------------
        <BLANKLINE>
            Target attribute `custom_output'
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
                custom_output = 0
        <BLANKLINE>
          Rule 2: [94 cases, mean 1.5, range 1 to 2, est err 0.2]
        <BLANKLINE>
            if
                petal width (cm) > 0.6
            then
                custom_output = 0.2 + 0.76 petal width (cm) + 0.271 petal length (cm)
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
        Cubist(n_rules=2, target_label='custom_output', verbose=True)

Model Construction
==================

These parameters control the model structure.

n_rules
-------

Varying the ``n_rules`` parameter changes the maximum number of rules Cubist will generate for a model. Recall the definition of a rule from the :ref:`Introduction<index:Background>`.

n_committees
------------

Varying the ``n_committees`` parameter changes the number of models (called committees) Cubist will generate. Recall the definition of a committee from the :ref:`Introduction<index:Background>`.

neighbors
---------

Varying the ``neighbors`` parameter changes the number of nearest neighbors Cubist will use to correct the rule-based prediction. Using this feature may improve accuracy at the cost of interpretability as the linear models won't be completely followed. Additionally the training dataset will be cached in the model to support future predictions.

unbiased
--------

Toggling ``unbiased`` determines whether to allow the mean predicted value for the training cases covered by a rule to differ from their mean value. The default is to minimize the average absolute error.

extrapolation
-------------

Varying the ``extrapolation`` parameter changes the percentage outside of the output values seen in the training dataset to which Cubist can extrapolate.


Alternative Modes
=================

These parameters control the mode in which the model is being used. The standard behavior is to train the model given the model tuning settings or their respective defaults.

auto
----

Cubist can be allowed to determine whether to introduce instance-based corrections with a composite model by leaving ``neighbors`` unset and setting ``auto=True``. This feature may increase training time and may produce a warning with regards to Cubist's recommendation. This can be effective as an initial experiment to consider the benefits of a composite model.

sample
------

When training on a large dataset, Cubist can subsample from the training dataset with the training percentage set by the ``sample`` parameter.

cv
--


random_state
------------

Setting a value for ``random_state`` sets the random seed for Cubist to enable repeatable cross-validation and sampling.
