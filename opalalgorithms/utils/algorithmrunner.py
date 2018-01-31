"""Given an algorithm object, run the algorithm."""
from __future__ import division, print_function
import multiprocessing as mp
import random
import time
import os
import math
import bandicoot
import csv

__all__ = ["AlgorithmRunner"]


def mapper(writing_queue, params, users_csv_files, algorithmobj):
    """Map user_data to result.

    Args:
        writing_queue (mp.manager.Queue): Queue for inserting results.
        params (dict): Parameters to be used by each map of the algorithm.
        users_csv_files (list): List of paths of csv files of users.
        algorithmobj (opalalgorithm.core.OPALAlgorithm): OPALAlgorithm object.
    """
    for user_csv_file in users_csv_files:
        username = os.path.splitext(os.path.basename(user_csv_file))[0]
        bandicoot_user = bandicoot.read_csv(username, os.path.dirname(user_csv_file))
        result = algorithmobj.map(params, bandicoot_user)
        writing_queue.put(result)


def collector(writing_queue, results_csv_path):
    """Collect the results in writing queue in a single csv.

    Args:
        writing_queue (mp.manager.Queue): Queue from which collect results.
        results_csv_path (str): CSV where we have to save results.
    """
    #TODO rewrite to send the collected result to the aggregation+privacy service
    with open(results_csv_path, 'a') as csvfile:
        while True:
            # wait for result to appear in the queue
            map = writing_queue.get()
            # if got signal 'kill' exit the loop
            if map == 'kill':
                break
            if map is not None:
                csvfile.write(map, delimiter=' ', lineterminator='\n')


#  Useless change in design with reduce being done at the aggregation service
# def reducer(params, results_csv_file):
#     """Reduce the results from a csv to a single number.
#
#     Args:
#         params (dict): Parameters to be used by the reduce of the algorithm.
#         results_csv_file (str): CSV Path where results are saved.
#     """
#     params["aggregation"]
#     aggregation = dict()
#     with open(results_csv_file, 'r') as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=' ')
#         for row in csv_reader:
#             a = str(row[1])
#             if a in aggregation:
#                 aggregation[a] += 1
#             else:
#                 aggregation[a] = 1
#     return aggregation


class AlgorithmRunner(object):
    """Algorithm runner.

    Args:
        algorithmobj (OPALAlgorithm): Instance of an opal algorithm.

    """

    def __init__(self, algorithmobj):
        """Initialize class."""
        self.algorithmobj = algorithmobj

    def __call__(self, params, data_dir, num_threads, results_csv_path):
        """Run algorithm.

        Args:
            params (dict): Dictionary containing all the parameters for the algorithm
            data_dir (str): Data directory.
            num_threads (int): Number of threads
            results_csv_path (str): Path where to save results in csv.
        """
        start_time = time.time()
        csv_files = [os.path.join(
            os.path.abspath(data_dir), f) for f in os.listdir(data_dir)
            if f.endswith('.csv')]
        sampling = round(params["sampling"] * len(csv_files))
        sampled_csv_files = random.sample(csv_files, sampling)
        step_size = int(math.ceil(len(sampled_csv_files) / num_threads))
        chunks_list = [sampled_csv_files[j:min(j + step_size, len(sampled_csv_files))]
                       for j in range(0, len(sampled_csv_files), step_size)]

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
                writing_queue, params, chunks_list[i], self.algorithmobj)))
            i += 1

        # Clean up parallel processing (close pool, wait for processes to
        # finish, kill writing_queue, wait for queue to be killed)
        pool.close()
        for job in jobs:
            job.get()
        writing_queue.put('kill')  # stop collection
        pool.join()
        # result = reducer(params, results_csv_path)  # Move it to the aggregation/privacy module
        elapsed_time = time.time() - start_time
        return elapsed_time
