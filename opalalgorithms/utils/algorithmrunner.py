"""Given an algorithm object, run the algorithm."""
from __future__ import division, print_function
import multiprocessing as mp
import random
import time
import os
import math
import bandicoot
import six

__all__ = ["AlgorithmRunner"]


def mapper(writing_queue, params, users_csv_files, algorithmobj,
           dev_mode=False):
    """Call the map function and insert result into the queue if valid.

    Args:
        writing_queue (mp.manager.Queue): Queue for inserting results.
        params (dict): Parameters to be used by each map of the algorithm.
        users_csv_files (list): List of paths of csv files of users.
        algorithmobj (opalalgorithm.core.OPALAlgorithm): OPALAlgorithm object.
        dev_mode (bool): Development mode.

    """
    for user_csv_file in users_csv_files:
        username = os.path.splitext(os.path.basename(user_csv_file))[0]
        bandicoot_user = bandicoot.read_csv(username, os.path.dirname(
            user_csv_file), describe=dev_mode, warnings=dev_mode)
        result = algorithmobj.map(params, bandicoot_user)
        if result:
            if is_valid_result(result):
                writing_queue.put(result)
            elif dev_mode:
                print("Error in result {}".format(result))


def collector(writing_queue, params, dev_mode=False):
    """Collect the results in writing queue and post to aggregator.

    Args:
        writing_queue (mp.manager.Queue): Queue from which collect results.
        results_csv_path (str): CSV where we have to save results.
        dev_mode (bool): Whether to run algorithm in development mode.

    Notes:
        If `dev_mode` is set to true, then collector will just read the result
        but do nothing.

    """
    while True:
        # wait for result to appear in the queue
        result = writing_queue.get()
        # if got signal 'kill' exit the loop
        if result == 'kill':
            break
        if result is not None:
            if dev_mode:
                print("posting result to aggregator {}".format(result))
            else:
                # TODO: Post to aggregator
                pass


def is_valid_result(result):
    """Check if result is valid.

    Args:
        result: Output of the algorithm.

    Note:
        Result is valid if it is a dict. All keys of the dict must be
        be a point or string. All points must be 1d or all must be 2d.
        All values must be numbers. These results are sent to reducer
        which will sum, mean, median, mode of the values belonging to same key.

        Example:
            - {"alpha1": 1, "ant199": 1, ..}
            - {(231, 283): 1, (154, 87): 0.5, ..}
            - {(1): 7, (356): 6, ..}

    Returns:
        bool: Specifying if the result is valid or not.

    Todo:
        * String as key has privacy concerns, might need to change later.

    """
    # check result must be a dict
    if not isinstance(result, dict):
        return False
    # check each value must be an integer or float
    if not (all([isinstance(x, six.integer_types) or isinstance(x, float)
                 for x in six.itervalues(result)])):
        return False
    # check each key must either be a string or tuple, a dict cannot have some
    # keys as string and some as tuple. If it is tuple then all keys must
    # either be of length 1 or length 2.
    if not ((all([isinstance(x, tuple) and len(x) == 2
                  for x in six.iterkeys(result)]) or
             all([isinstance(x, tuple) and len(x) == 1
                  for x in six.iterkeys(result)])) or
            all([isinstance(x, six.string_types)
                 for x in six.iterkeys(result)])):
        return False
    return True


class AlgorithmRunner(object):
    """Algorithm runner.

    Args:
        algorithmobj (OPALAlgorithm): Instance of an opal algorithm.
        dev_mode (bool): Development mode switch

    """

    def __init__(self, algorithmobj, dev_mode=False):
        """Initialize class."""
        self.algorithmobj = algorithmobj
        self.dev_mode = dev_mode

    def __call__(self, params, data_dir, num_threads):
        """Run algorithm.

        Selects the csv files from the data directory. Samples data from
        the csv files based on sampling rate. Divides the sampled csv files
        into chunks of equal size across the `num_threads` threads. Each thread
        performs calls map function of the csv file and processes the result.
        The collector thread, waits for results before posting it to aggregator
        service.

        Args:
            params (dict): Dictionary containing all the parameters for the
                algorithm
            data_dir (str): Data directory with csv files.
            num_threads (int): Number of threads

        Returns:
            int: Amount of time required for computation in microseconds.

        """
        start_time = time.time()
        csv_files = [os.path.join(
            os.path.abspath(data_dir), f) for f in os.listdir(data_dir)
            if f.endswith('.csv')]
        sampling = int(math.ceil(params["sampling"] * len(csv_files)))
        sampled_csv_files = random.sample(csv_files, sampling)
        step_size = int(math.ceil(len(sampled_csv_files) / num_threads))
        chunks_list = [sampled_csv_files[j:min(j + step_size, len(
                       sampled_csv_files))] for j in range(
                        0, len(sampled_csv_files), step_size)]

        # set up parallel processing
        manager = mp.Manager()
        writing_queue = manager.Queue()
        jobs = []

        # additional 1 process for writer
        pool = mp.Pool(processes=num_threads + 1)
        pool.apply_async(collector, (writing_queue, params, self.dev_mode))

        # Compute the density
        i = 0
        for thread_id in range(num_threads):
            jobs.append(pool.apply_async(mapper, (
                writing_queue, params, chunks_list[i], self.algorithmobj,
                self.dev_mode)))
            i += 1

        # Clean up parallel processing (close pool, wait for processes to
        # finish, kill writing_queue, wait for queue to be killed)
        pool.close()
        for job in jobs:
            job.get()
        writing_queue.put('kill')  # stop collection
        pool.join()
        elapsed_time = time.time() - start_time
        return elapsed_time
