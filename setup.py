from setuptools import setup
from Cython.Build import cythonize
from numpy.distutils.misc_util import Configuration
from distutils.core import Extension
import numpy as np
import os
import glob

os.environ["CXX"] = "g++-9"


def configuration(parent_package='', top_path=None):
    config = Configuration(None, parent_package, top_path)
    config.add_subpackage('cubist_src')
    return config


exts = [Extension(name='cubist',
                  sources=["cubist/_cubist.pyx"] + glob.glob("cubist/src/*.c") + glob.glob("cubist/src/*.cpp"),
                  include_dirs=[np.get_include(), "cubist/src"])]


if __name__ == "__main__":
    setup(
        name="cubist",
        ext_modules=cythonize(exts),
        zip_safe=False,
        # configuration=configuration,
        include_package_data=True
    )
