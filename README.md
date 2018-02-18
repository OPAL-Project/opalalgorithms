# OPAL Algorithms

Algorithms for OPAL Project. This repo contains python library of algorithms being used in OPAL Project. To implement any new algorithm, install this library, create a new class by inheriting the base class. Implement `map`
and `reduce` functions.

## Installation

OPALAlgorithms works both in python 2.7 and python 3.6 environments. Before proceeding it is strictly recommended you activate virtualenv of python 2.7 or python 3.6 .To install follow the following steps:

```bash
git clone https://github.com/shubhamjain0594/opalalgorithms.git
cd opalalgorithms
pip install -r requirements.txt
python setup.py install
```

To run tests

```bash
cd tests
bash test.sh
```

## Usage Instructions

This library is to be used for writing new algorithms to be run on OPAL Platform. To write any new algorithm, you will have to inherit `opal.core.OPALAlgorithm` and implement `map` function. Ensure that you do not import any functions from external file and all the helper functions are available in the single file containing Algorithm class.

`map` function will get `params` which are the parameters of the request and (`bandicoot_user`)[http://bandicoot.mit.edu/docs/reference/generated/bandicoot.User.html#bandicoot.User]

Also do ensure that you do not install any packages, except the ones installed by the opalalgorithm package.

A sample algorithm implementation for finding population density can be found at `tests/sample_algos/algo1.py`.

Use `tests/generate_data.py` for generating synthetic data for testing. Take a look at `tests/test.sh` and `tests/test_algos.py` to check how to test your algorithm implementation.

## Documentation

Please find hosted documentation [here](http://opalalgorithms.readthedocs.io/en/latest/index.html).

## TODO

- Flake8 and coding standard checks

## Notes