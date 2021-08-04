from setuptools import setup, Extension
from Cython.Build import cythonize
import glob
import numpy as np
import os.path
import codecs

extensions = [
    Extension(
        name='_cubist',
        sources=["cubist/_cubist.pyx"] + glob.glob("cubist/src/*.c"),
        include_dirs=["cubist/src", np.get_include()]
    )
]

with open("README.md", 'r') as f:
    long_description = f.read()

with open("requirements.txt", 'r') as f:
    requires = f.read()

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="cubist",
    version=get_version("cubist/__init__.py"),
    author="Patrick Aselin",
    description="A Python wrapper to Quinlan's Cubist regression model.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    ext_modules=cythonize(extensions),
    zip_safe=False,
    include_package_data=True,
    install_requires=requires,
    url="https://github.com/pjaselin/Cubist",
    packages=["cubist"],
    license="LICENSE",
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research"
    ]
)
