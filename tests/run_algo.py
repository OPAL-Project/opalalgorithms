"""Test population density algorithm."""
from __future__ import division, print_function
from opalalgorithms.utils import AlgorithmRunner


num_threads = 3
data_path = 'data'


def get_algo(filename):
    algorithm = dict(
        code=open(filename).read(),
        className='SampleAlgo1'
    )
    return algorithm


def run_algo(algorithm_filename, params):
    """Run an algorithm."""
    algorithm = get_algo(algorithm_filename)
    algorunner = AlgorithmRunner(
        algorithm, dev_mode=False, multiprocess=True, sandboxing=True)
    result = algorunner(params, data_path, num_threads)
    return result


if __name__ == '__main__':
    """Test that algorithm runner runs successfully."""
    params = dict(
        sample=0.2,
        aggregation_level='location_level_1')
    assert run_algo('sample_algos/algo1.py', params)
