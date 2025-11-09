import glob
import sys

import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup

extra_compile_args: list[str] = []
if sys.platform == "darwin":
    extra_compile_args.extend(
        [
            "-Wno-error=int-conversion",  # For snprintf issues in implicitatt.c
            "-Wno-unused-but-set-variable",  # For Bestid in formrules.c
        ]
    )


extensions = [
    Extension(
        name="_cubist",
        sources=["cubist/_cubist.pyx"] + glob.glob("cubist/src/*.c"),
        include_dirs=["cubist/src", np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        extra_compile_args=extra_compile_args,
    )
]

setup(
    ext_modules=cythonize(
        extensions, compiler_directives={"language_level": 3, "profile": False}
    ),
)
