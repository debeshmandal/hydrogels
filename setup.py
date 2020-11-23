import setuptools
from distutils.core import setup, Extension
from distutils import sysconfig
import os

with open("README.md", "r") as f:
    long_description = f.read()

cpp_args = ['-std=c++11']#, '-stdlib=libc++']#, '-mmacosx-version-min=10.7']

class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __str__(self):
        import pybind11
        return pybind11.get_include()

potentials = Extension(
    'potentials', sources = ['./hydrogels/theory/models/_cxx/potentials.cpp'],
    include_dirs=[get_pybind_include(), './hydrogels/theory/models/_cxx/'],
    language='c++',
    extra_compile_args = cpp_args,
    )

functions = Extension(
    'functions', sources = ['./hydrogels/theory/models/_cxx/functions.cpp'],
    include_dirs=[get_pybind_include(), './hydrogels/theory/models/_cxx/'],
    language='c++',
    extra_compile_args = cpp_args,
    )

setuptools.setup(
    name="hydrogels",
    version="0.5.0",
    author="Debesh Mandal",
    description="Package for creating and analysing hydrogels in ReaDDy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/debeshmandal/hydrogels",
    packages=['hydrogels'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
    ],
    python_requires=">=3.6",
    ext_package='hydrogels',
    ext_modules=[potentials, functions]
)
