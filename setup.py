from setuptools import setup, Extension
from Cython.Build import cythonize
import glob
import numpy as np

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

setup(
    name="cubist",
    version="0.0.9",
    author="Patrick Aselin",
    description="A Python port of the R Cubist library.",
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
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research"
    ]
)
