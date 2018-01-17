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
    results_csv_path = str(sys.argv[3])
    algorunner = AlgorithmRunner(algorithmobj)
    result = algorunner(data_dir, number_of_threads, results_csv_path)
    print(result)


if __name__ == "__main__":
    test_algos()
