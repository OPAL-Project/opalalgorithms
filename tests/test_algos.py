"""Test population density algorithm."""
from __future__ import division, print_function
import sys
from opalalgorithms.utils import AlgorithmRunner


def test_algos():
    """Main function."""
    # load the algorithm
    mod = __import__('sample_algos.algo1', fromlist=['SampleAlgo1'])
    algorithmclass = getattr(mod, 'SampleAlgo1')
    algorithmobj = algorithmclass()

    data_dir = str(sys.argv[1])
    number_of_threads = int(sys.argv[2])
    params = dict(sampling=0.2)
    algorunner = AlgorithmRunner(algorithmobj, dev_mode=True)
    result = algorunner(params, data_dir, number_of_threads)
    print(result)


if __name__ == "__main__":
    test_algos()
