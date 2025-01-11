.. cubist documentation master file, created by
   sphinx-quickstart on Sun Jan  5 14:13:50 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

cubist Documentation
====================

``cubist`` is a Python package and wrapper for Ross Quinlan's [Cubist](https://www.rulequest.com/cubist-unix.html) v2.07 regression model. It is inspired and based on [R wrapper](https://github.com/topepo/Cubist) for Cubist. It is also developed as a [scikit-learn](https://scikit-learn.org/stable/) compatible estimator.

Acknowledgements

Grateful to Kirk Mettler for introducing me to the model
Quinlan for his work on the model
Max Kuhn for developing the R package on which this is based


Background


Advantages

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting_started/install

.. toctree::
   :maxdepth: 2
   :caption: Usage

   usage/cubist
   usage/visualizations

.. toctree::
   :maxdepth: 2
   :caption: API

   api/cubist
   api/cubist_coefficient_display
   api/cubist_coverage_display
   api/exceptions
