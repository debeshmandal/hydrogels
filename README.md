# hydrogels

[![Manylinux](https://github.com/debeshmandal/hydrogels/workflows/ManyLinux/badge.svg)](https://github.com/debeshmandal/hydrogels/actions?query=workflow%3ALinux)
[![MacOS](https://github.com/debeshmandal/hydrogels/workflows/MacOS/badge.svg)](https://github.com/debeshmandal/hydrogels/actions?query=workflow%3AMacOS)
[![Coverage](https://codecov.io/github/debeshmandal/hydrogels/coverage.svg?branch=master)](https://codecov.io/gh/debeshmandal/hydrogels)

## Simulation and Numerical Integration for Hydrogel Degradation

This repository contains a variety of tools for simulating hydrogels. The main part of the code is for generating configurations and simulation systems for use with the software package called ReaDDy.

Then, in the `theory` folder, a numerical integration framework for integrating differential equations can be found. This is used for describing the enzymatic degradation of a hydrogel nanoparticle. This module in particular contains C++/Python code that is bound using `pybind11`. Also contained in the main repository, are Jupyter Notebooks with examples of how to use the `hydrogels.theory` module.

### Pre-requisites:

`hydrogels` is available on Linux, MacOS and Windows using Python `3.6`, `3.7`, `3.8`, and `3.9`.

At the time of writing it is only possible to install the package on a Linux architecture. This requires the following prerequisites:
  - `gxx`
  - `pybind11`
  - `numpy`
  - `pandas`
  - [`readdy`](https://github.com/readdy/readdy)
  - `scipy`
  - `networkx`
  - [`softnanotools`](https://github.com/softnanolab/softnanotools)
  - [`starpolymers`](https://github.com/debeshmandal/starpolymers)

Installing most these packages is generally trivial and can be done using either `pip` or `anaconda`. However install `readdy` is typically done only by using `anaconda`.

```bash
# optional - only add if you don't have it already
conda config --add channels conda-forge

# install readdy
conda install -c readdy readdy
```

In our continuous integration, we provide a method for installing `readdy` via `pip`, but in some environments, in particular on local machines, problems locating `HDF5` can arise, hence we recommend using `conda` instead. Here is how to build `readdy` manually using `pip`:

```bash
git clone https://github.com/readdy/readdy
pushd readdy
pip install .
popd
```

### Installing `hydrogels`

To install, do the following command from the main directory:

```bash
pip install .
```

And to test (also from the main directory):


```bash
pytest --import-mode=importlib
```

