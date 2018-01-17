"""Given an algorithm object, run the algorithm."""
from __future__ import division, print_function
import multiprocessing as mp
import time
import os
import math

__all__ = ["AlgorithmRunner"]


def mapper(writing_queue, users_csv_files, algorithmobj):
    """Map user_data to result.

    Args:
        writing_queue (mp.manager.Queue): Queue for inserting results.
        users_csv_files (list): List of paths of csv files of users.
        algorithmobj (opalalgorithm.core.OPALAlgorithm): OPALAlgorithm object.
    """
    for user_csv_file in users_csv_files:
        username = os.path.splitext(os.path.basename(user_csv_file))[0]
        result = algorithmobj.map(user_csv_file)
        writing_queue.put((username, result))


def collector(writing_queue, results_csv_path):
    """Collect the results in writing queue in a single csv.

    Args:
        writing_queue (mp.manager.Queue): Queue from which collect results.
        results_csv_path (str): CSV where we have to save results.
    """
    with open(results_csv_path, 'a') as csvfile:
        while True:
            # wait for result to appear in the queue
            user = writing_queue.get()
            # if got signal 'kill' exit the loop
            if user == 'kill':
                break
            if user is not None:
                csvfile.write(user[0] + ' ' + user[1] + '\n')


def reducer(algorithmobj, results_csv_path):
    """Reduce the results from a csv to a single number.

    Args:
        algorithmobj (opalalgorithm.core.OPALAlgorithm): OPALAlgorithm object.
        results_csv_path (str): CSV Path where results are saved.
    """
    return algorithmobj.reduce(results_csv_path)


class AlgorithmRunner(object):
    """Algorithm runner.

    Args:
        algorithmobj (OPALAlgorithm): Instance of an opal algorithm.

    """

    def __init__(self, algorithmobj):
        """Initialize class."""
        self.algorithmobj = algorithmobj

    def __call__(self, data_dir, num_threads, results_csv_path):
        """Run algorithm.

        Args:
            data_dir (str): Data directory.
            num_threads (int): Number of threads
            results_csv_path (str): Path where to save results in csv.
        """
        start_time = time.time()
        csvfiles = [os.path.join(
            os.path.abspath(data_dir), f) for f in os.listdir(data_dir)
            if f.endswith('.csv')]
        step_size = int(math.ceil(len(csvfiles) / num_threads))
        chunks_list = [csvfiles[j:min(j+step_size, len(csvfiles))]
                       for j in range(0, len(csvfiles), step_size)]

        # set up parallel processing
        manager = mp.Manager()
        writing_queue = manager.Queue()
        jobs = []

        # additional 1 process for writer
        pool = mp.Pool(processes=num_threads + 1)
        pool.apply_async(collector, (writing_queue, results_csv_path,))

        # Compute the density
        i = 0
        for thread_id in range(num_threads):
            jobs.append(pool.apply_async(mapper, (
                writing_queue, chunks_list[i], self.algorithmobj)))
            i += 1

        # Clean up parallel processing (close pool, wait for processes to
        # finish, kill writing_queue, wait for queue to be killed)
        pool.close()
        for job in jobs:
            job.get()
        writing_queue.put('kill')  # stop collection
        pool.join()
        result = reducer(self.algorithmobj, results_csv_path)
        elapsed_time = time.time() - start_time
        print("The algorithm computation is done and it took: {}".format(
            elapsed_time))
        return result
