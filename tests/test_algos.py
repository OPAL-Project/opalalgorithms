"""Test population density algorithm."""
from __future__ import division, print_function
import sys
from opalalgorithms.utils import AlgorithmRunner


def test_algos():
    """Main function."""
    # load the algorithm
    code_string = open('sample_algos/algo1.py').read()
    data_dir = str(sys.argv[1])
    number_of_threads = int(sys.argv[2])
    params = dict(
        sampling=0.2,
        aggregation_level='location_level_1')
    algorunner = AlgorithmRunner(code_string, 'SampleAlgo1', dev_mode=False)
    result = algorunner(params, data_dir, number_of_threads)
    print(result)


if __name__ == "__main__":
    test_algos()
