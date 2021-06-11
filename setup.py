from setuptools import setup
from Cython.Build import cythonize
from numpy.distutils.misc_util import Configuration
from distutils.core import Extension
import numpy as np
import os
import glob

# os.environ["CXX"] = "g++-9"
os.environ["CC"] = "gcc"


def configuration(parent_package='', top_path=None):
    config = Configuration(None, parent_package, top_path)
    config.add_subpackage('cubist_src')
    return config


exts = [Extension(name='_cubist',
                  sources=["cubist/_cubist.pyx"] + glob.glob("cubist/src/*.c"),
                  include_dirs=["cubist/src"])]


if __name__ == "__main__":
    setup(
        name="cubist",
        ext_modules=cythonize(exts),
        zip_safe=False,
        # configuration=configuration,
        include_package_data=True
    )
