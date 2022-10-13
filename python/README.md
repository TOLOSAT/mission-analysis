# Mission Analysis in Python

## Tudatpy

The TU Delft Astrodynamics Toolbox in Python, or tudatpy, is a python library that primarily exposes the powerful set
of [Tudat](https://tudat.tudelft.nl/) C++ libraries for orbit propagation.

The Tudat documentation is available [here](https://docs.tudat.space/en/stable/). The tudatpy API reference is
available [here](https://py.api.tudat.space/en/latest/).

## Installation

**--------> A MORE DETAILED SETUP GUIDE IS AVAILABLE [HERE](setup_guide/README.md). <--------**

It is recommended to use [Anaconda](https://www.anaconda.com/) (includes Spyder, jupyter notebooks, etc.)
or [Miniforge](https://github.com/conda-forge/miniforge) (lightweight alternative with `conda` only).

You can install tudatpy in a new dedicated environment called `tolosat-tudatpy` by navigating to this directory and
running the following command:

```
conda env create -f environment.yaml
```

Any missing package beyond this step (like `TLE-tools`) can be installed by running the Anaconda/Miniforge prompt and
running the following commands: `conda activate tolosat-tudatpy` and then `conda install <package_name>`
or `pip install <package_name>`.

## Python IDE

The recommended IDE is [PyCharm](https://www.jetbrains.com/pycharm/). A professional license is provided for free to
students by applying [here](https://www.jetbrains.com/shop/eform/students).

The Python interpreter should be configured to use the `tolosat-tudatpy` environment.

When opening the full `mission-analysis` project in PyCharm, use *right-click > Mark Directory as > Sources Root* on
the `python` folder.



