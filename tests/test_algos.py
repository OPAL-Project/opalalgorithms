"""Test population density algorithm."""
from __future__ import division, print_function
import sys
from opalalgorithms.utils import AlgorithmRunner


def test_algos():
    """Main function."""
    # load the algorithm
    # mod = __import__('sample_algos.algo1', fromlist=['SampleAlgo1'])
    # algorithmclass = getattr(mod, 'SampleAlgo1')
    # algorithmobj = algorithmclass()
    total_time = 0
    num_times = int(sys.argv[3])
    for i in range(num_times):
        algorithm = dict(
            code=open('sample_algos/algo1.py').read(),
            className='SampleAlgo1'
        )

        data_dir = str(sys.argv[1])
        number_of_threads = int(sys.argv[2])
        params = dict(
            sampling=0.2,
            aggregation_level='location_level_1')
        algorunner = AlgorithmRunner(
            algorithm, dev_mode=False, multiprocess=False, sandboxing=False)
        result = algorunner(params, data_dir, number_of_threads)
        print(i, result)
        total_time += result
    print(total_time / num_times)


if __name__ == "__main__":
    test_algos()
