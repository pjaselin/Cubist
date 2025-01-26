Cubist Model
#####

The Cubist model class (``cubist.Cubist``) has eleven parameters and eleven attributes available. Their example usage is demonstrated below and the class is documented in the API Docs section at :ref:`api/model:Cubist`.

Parameters
**********

These are the values passed to the model at class initialization.

Display Options
===============

These parameters change or allow for viewing Cubist's model report.

target_label
------------

As the pretty-printed result includes a name for the target (y) value, the ``target_label`` parameter can be set to change the target label to something other than the default of `outcome`.

verbose
-------

The ``verbose`` flag indicates whether Cubist should pretty-print the generate model, summary, and training performance to the console. Either an integer or Python boolean is accepted.

.. dropdown:: Sample Output with Custom Target Label

    Dropdown content

Model Tuning
============

These parameters control the type and complexity of the model.

n_rules
-------

n_committees
------------

neighbors
---------

unbiased
--------

extrapolation
-------------

random_state
------------

Alternative Modes
=================

These parameters control the mode in which the model is being used. The standard behavior is to train the model given the model tuning settings or their respective defaults.

auto
----

sample
------

cv
--

Whether

Simple n_rules

.. code-block:: python

    >>> from cubist import Cubist

    >>> model = Cubist()

    >>> msg = msgspec.json.encode(alice)

    >>> msg
    b'{"name":"alice","groups":["admin","engineering"],"email":null}'

.. dropdown::

    Dropdown content

With committees

with instance-based correction

auto mode

Cross-validation

verbose

sampling

extrapolation

Attributes
**********
