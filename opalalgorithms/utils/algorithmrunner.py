"""Given an algorithm object, run the algorithm."""
from __future__ import division, print_function
import multiprocessing as mp
import random
import time
import os
import math
import six
import codejail
from codejail.safe_exec import not_safe_exec
from codejail.limits import set_limit
import textwrap

__all__ = ["AlgorithmRunner"]


def get_jail():
    """Return codejail object.

    Note:
        - Please set environmental variables `OPALALGO_SANDBOX_VENV`
            and `OPALALGO_SANDBOX_USER` before calling this function.
        - `OPALALGO_SANDBOX_VENV` must be set to the path of the sandbox
            virtual environment.
        - `OPALALGO_SANDBOX_USER` must be set to the user running the
            sandboxed algorithms.
    """
    sandbox_env = os.environ.get('OPALALGO_SANDBOX_VENV')
    sandbox_user = os.environ.get('OPALALGO_SANDBOX_USER')
    set_limit("REALTIME", None)
    jail = codejail.configure(
        'python',
        os.path.join(sandbox_env, 'bin', 'python'),
        user=sandbox_user)
    jail = codejail.get_codejail('python')
    return jail


def process_user_csv(params, user_csv_file, algorithm, dev_mode, sandboxing,
                     jail):
    """Process a single user csv file.

    Args:
        params (dict): Parameters for the request.
        user_csv_file (string): Path to user csv file.
        algorithm (dict): Dictionary with keys `code` and `className`
            specifying algorithm code and className.
        dev_mode (bool): Should the algorithm run in development mode or
            production mode.
        sandboxing (bool): Should sandboxing be used or not.
        jail (codejail.Jail): Jail object.

    Returns:
        Result of the execution.

    Raises:
        SafeExecException: If the execution wasn't successful.

    """
    username = os.path.splitext(os.path.basename(user_csv_file))[0]
    globals_dict = {
        'params': params,
    }
    user_specific_code = textwrap.dedent(
        """
        def run_code():
            import bandicoot

            algorithmobj = {}()
            bandicoot_user = bandicoot.read_csv(
               '{}', '', describe={}, warnings={})
            return algorithmobj.map(params, bandicoot_user)
        result = run_code()
        """.format(
            algorithm['className'], username, str(dev_mode), str(dev_mode),
            os.path.basename(user_csv_file)))
    code = "{}\n{}".format(algorithm['code'], user_specific_code)
    if sandboxing:
        jail.safe_exec(
            code, globals_dict, files=[user_csv_file])
    else:
        not_safe_exec(
            code, globals_dict, files=[user_csv_file])
    result = globals_dict['result']
    return result


def process(params, users_csv_files, algorithm, dev_mode, sandboxing):
    """Process files as per arguments.

    Args:
        params (dict): Parameters for the request.
        users_csv_files (list): List of paths to user csv files.
        algorithm (dict): Dictionary with keys `code` and `className`
            specifying algorithm code and className.
        dev_mode (bool): Should the algorithm run in development mode or
            production mode.
        sandboxing (bool): Should sandboxing be used or not.

    """
    jail = get_jail()
    for user_csv_file in users_csv_files:
        yield process_user_csv(
            params, user_csv_file, algorithm, dev_mode,
            sandboxing, jail)


def mapper(writing_queue, params, users_csv_files, algorithm,
           dev_mode=False, sandboxing=True):
    """Call the map function and insert result into the queue if valid.

    Args:
        writing_queue (mp.manager.Queue): Queue for inserting results.
        params (dict): Parameters to be used by each map of the algorithm.
        users_csv_files (list): List of paths of csv files of users.
        algorithm (dict): Dictionary with keys `code` and `className`
            specifying algorithm code and className.
        dev_mode (bool): Should the algorithm run in development mode or
            production mode.
        sandboxing (bool): Should sandboxing be used or not.
    """
    for result in process(params, users_csv_files, algorithm, dev_mode,
                          sandboxing):
        if result:
            if is_valid_result(result):
                writing_queue.put(result)
            elif dev_mode:
                print("Error in result {}".format(result))


def process_result(result, params, dev_mode):
    if result is not None:
        if dev_mode:
            print("posting result to aggregator {}".format(result))
        else:
            # TODO: Post to aggregator
            pass


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
        process_result(result, params, dev_mode)


def is_valid_result(result):
    """Check if result is valid.

    Args:
        result: Output of the algorithm.

    Note:
        Result is valid if it is a dict. All keys of the dict must be
        be a string. All values must be numbers. These results are sent to
        reducer which will sum, count, mean, median, mode of the values
        belonging to same key.

        Example:
            - {"alpha1": 1, "ant199": 1, ..}

    Returns:
        bool: Specifying if the result is valid or not.

    Todo:
        * Define what is valid with privacy and other concerns

    """
    # check result must be a dict
    if not isinstance(result, dict):
        return False
    # check each value must be an integer or float
    if not (all([isinstance(x, six.integer_types) or isinstance(x, float)
                 for x in six.itervalues(result)])):
        return False
    # check each key must be a string.
    if not (all([isinstance(x, six.string_types)
                 for x in six.iterkeys(result)])):
        return False
    return True


class AlgorithmRunner(object):
    """Algorithm runner.

    Args:
        algorithm (dict): Dictionary containing `code` and `className`.
        dev_mode (bool): Development mode switch
        multiprocess (bool): Use multiprocessing or single process for
            complete execution.
        sandboxing (bool): Use sandboxing for execution or execute in unsafe
            environment.

    """

    def __init__(self, algorithm, dev_mode=False, multiprocess=True,
                 sandboxing=True):
        """Initialize class."""
        self.algorithm = algorithm
        self.dev_mode = dev_mode
        self.multiprocess = multiprocess
        self.sandboxing = sandboxing

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
        if self.multiprocess:
            self._multiprocess(params, num_threads, sampled_csv_files)
        else:
            self._singleprocess(params, num_threads, sampled_csv_files)

        elapsed_time = time.time() - start_time
        return elapsed_time

    def _multiprocess(self, params, num_threads, csv_files):
        step_size = int(math.ceil(len(csv_files) / num_threads))
        chunks_list = [csv_files[j:min(j + step_size, len(
                       csv_files))] for j in range(
                        0, len(csv_files), step_size)]

        # set up parallel processing
        manager = mp.Manager()
        writing_queue = manager.Queue()
        jobs = []

        # additional 1 process for writer
        pool = mp.Pool(processes=num_threads + 1)
        pool.apply_async(collector, (writing_queue, params, self.dev_mode))

        # Compute the density
        for chunk in chunks_list:
            jobs.append(pool.apply_async(mapper, (
                writing_queue, params, chunk, self.algorithm, self.dev_mode,
                self.sandboxing)))

        # Clean up parallel processing (close pool, wait for processes to
        # finish, kill writing_queue, wait for queue to be killed)
        pool.close()
        for job in jobs:
            job.get()
        writing_queue.put('kill')  # stop collection
        pool.join()

    def _singleprocess(self, params, num_threads, csv_files):
        for result in process(params, csv_files, self.algorithm,
                              self.dev_mode, self.sandboxing):
            process_result(result, params, self.dev_mode)
