Cubist Model
#####

The Cubist model class (``cubist.Cubist``) has eleven parameters available. Their use is documented below.

Display Options
===============

verbose
-------

target_label
------------

Model Tuning
============

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
