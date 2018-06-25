"""Test population density algorithm."""
from __future__ import division, print_function
from opalalgorithms.utils import AlgorithmRunner
import codejail
import pytest
import subprocess
import time
import signal


num_threads = 3
data_path = 'data'


def get_algo(filename, class_name='SampleAlgo1'):
    """Get algorithm to run."""
    algorithm = dict(
        code=open(filename).read(),
        className=class_name
    )
    return algorithm


def run_algo(algorithm_filename, params, dev_mode=True):
    """Run an algorithm."""
    algorithm = get_algo(algorithm_filename)
    algorunner = AlgorithmRunner(
        algorithm, dev_mode=dev_mode, multiprocess=True, sandboxing=True)
    return algorunner(params, data_path, num_threads)


def test_algo_success():
    """Test that algorithm runner runs successfully."""
    params = dict(
        sample=0.2,
        resolution='location_level_1')
    result = run_algo('sample_algos/algo1.py', params)
    assert type(result) is list


@pytest.mark.xfail(raises=codejail.exceptions.SafeExecException)
def test_algo_failure():
    """Check if codejail is working correctly."""
    params = dict(
        sample=0.2,
        resolution='location_level_1')
    assert run_algo('sample_algos/algo1.py', params)


def test_interrupt_works():
    """Check that algorithm exits with error on SIGINT."""
    proc = subprocess.Popen(['/bin/sh', '-c', 'python', 'run_algo.py'])
    time.sleep(1)
    proc.send_signal(signal.SIGINT)
    time.sleep(1)
    poll = proc.poll()
    assert poll is not None
