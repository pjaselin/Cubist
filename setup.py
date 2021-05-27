from setuptools import setup
from Cython.Build import cythonize
from numpy.distutils.misc_util import Configuration


def configuration(parent_package='', top_path=None):
    config = Configuration(None, parent_package, top_path)
    config.add_subpackage('cubist_src')
    return config


if __name__ == "__main__":
    setup(
        name="cubist",
        # ext_modules=cythonize(["cubist/devtest.pyx"]),
        zip_safe=False,
        configuration=configuration,
        include_package_data=True
    )
