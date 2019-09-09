"""Given an algorithm object, run the algorithm."""
from __future__ import division, print_function

import signal
import sys
import multiprocessing as mp
import os
import textwrap
import json

import requests
import six
import codejail
from codejail.safe_exec import not_safe_exec
from codejail.limits import set_limit


__all__ = ["AlgorithmRunner"]


class GracefulExit(Exception):
    """Graceful exit exception class."""


def sigint_handler(signum, thread):
    """Handle interrupt signal."""
    raise GracefulExit()


def check_environ():
    """Check that all environment variable exists.

    Note:
        - Required environment variables are `OPALALGO_SANDBOX_VENV` and
            `OPALALGO_SANDBOX_USER`.

    """
    req_environ_vars = ['OPALALGO_SANDBOX_VENV', 'OPALALGO_SANDBOX_USER']
    for environ_var in req_environ_vars:
        if environ_var not in os.environ:
            raise RuntimeError(
                'Environment variable {} not set'.format(environ_var))


def get_jail(python_version=sys.version_info[0]):
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
    set_limit("CPU", 15)
    codejail.configure(
        'python',
        os.path.join(sandbox_env, 'bin', 'python'),
        user=sandbox_user)
    codejail.configure(
        'python3',
        os.path.join(sandbox_env, 'bin', 'python'),
        user=sandbox_user)
    if python_version < 3:
        jail = codejail.get_codejail('python')
    else:
        jail = codejail.get_codejail('python3')
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
            algorithm['className'], username,
            str(dev_mode), str(dev_mode)))
    code = "{}\n{}".format(algorithm['code'], user_specific_code)
    if sandboxing:
        jail.safe_exec(
            code, globals_dict, files=[user_csv_file])
    else:
        not_safe_exec(
            code, globals_dict, files=[user_csv_file])
    result = globals_dict['result']
    return result


def mapper(writing_queue, params, file_queue, algorithm,
           dev_mode=False, sandboxing=True, python_version=2):
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
        python_version (int): Python version being used for sandboxing.

    """
    jail = get_jail(python_version)
    while not file_queue.empty():
        filepath = None
        scaler = None
        try:
            result = file_queue.get(timeout=1)
            filepath, scaler = result
        except Exception as exc:
            print(exc)
            break
        result = process_user_csv(
            params, filepath, algorithm, dev_mode,
            sandboxing, jail)
        if result and is_valid_result(result):
            writing_queue.put((result, scaler))
        elif result and dev_mode:
            print("Error in result {}".format(result))


def scale_result(result, scaler):
    """Return scaled result.

    Args:
        result (dict): Result.
        scaler (number): Factor by which results need to be scaled.

    Returns:
        dict: Scaled result.

    """
    scaled_result = {}
    for key, val in six.iteritems(result):
        scaled_result[key] = scaler * val
    return scaled_result


def collector(writing_queue, params, dev_mode=False):
    """Collect the results in writing queue and post to aggregator.

    Args:
        writing_queue (mp.manager.Queue): Queue from which collect results.
        results_csv_path (str): CSV where we have to save results.
        dev_mode (bool): Whether to run algorithm in development mode.

    Returns:
        bool: True on successful exit if `dev_mode` is set to False.

    Note:
        If `dev_mode` is set to true, then collector will just return all the
        results in a list format.

    """
    result_processor = ResultProcessor(params, dev_mode)
    while True:
        # wait for result to appear in the queue
        processed_result = writing_queue.get()
        # if got signal 'kill' exit the loop
        if processed_result == 'kill':
            break
        result, scaler = processed_result
        result_processor(result, scaler=scaler)
    return result_processor.get_result()


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


class ResultProcessor(object):
    """Process results.

    Args:
        params (dict): Dictionary of parameters.
        dev_mode (bool): Specify if dev_mode is on.

    """

    def __init__(self, params, dev_mode):
        """Initialize result processor."""
        self.params = params
        self.dev_mode = dev_mode
        self.result_list = []

    def __call__(self, result, scaler=1):
        """Process the result.

        If dev_mode is set to true, it appends the result to a list.
        Else it send the post request to `aggregationServiceUrl`.

        Args:
            result (dict): Result of the processed algorithm.
            scaler (int): Scale results by what value.

        """
        result = scale_result(result, scaler)
        if self.dev_mode:
            self.result_list.append(result)
        else:
            self._send_request(result)

    def _send_request(self, result):
        """Send request to aggregationServiceUrl.

        Args:
            result (dict): Result to be sent as an update.

        """
        response = requests.post(
            self.params['aggregationServiceUrl'], json={'update': result})
        if response.status_code != 200:
            raise RuntimeError(
                'Aggregation service returned {}'.format(
                    response.status_code))

    def get_result(self):
        """Return the result after processing.

        Returns:
            dict: if dev_mode is set to true else returns `True`

        """
        if self.dev_mode:
            return self.result_list
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

    def __call__(self, params, data_dir, num_threads, weights_file=None):
        """Run algorithm.

        Selects the csv files from the data directory. Divides the csv files
        into chunks of equal size across the `num_threads` threads. Each thread
        performs calls map function of the csv file and processes the result.
        The collector thread, waits for results before posting it to aggregator
        service.

        Args:
            params (dict): Dictionary containing all the parameters for the
                algorithm
            data_dir (str): Data directory with csv files.
            num_threads (int): Number of threads
            weights_file (str): Path to the json file containing weights.

        Returns:
            int: Amount of time required for computation in microseconds.

        """
        check_environ()
        csv_files = [os.path.join(
            os.path.abspath(data_dir), f) for f in os.listdir(data_dir)
                     if f.endswith('.csv')]
        csv2weights = self._get_weights(csv_files, weights_file)
        if self.multiprocess:
            return self._multiprocess(
                params, num_threads, csv_files, csv2weights)
        return self._singleprocess(params, csv_files, csv2weights)

    def _get_weights(self, csv_files, weights_file):
        """Return weights for each user if available, else return 1."""
        weights = None
        if weights_file:
            with open(weights_file) as file_path:
                weights = json.load(file_path)
        csv2weights = {}
        for file_path in csv_files:
            csv_weight = 1  # default weight
            user = os.path.splitext(os.path.basename(file_path))[0]
            if weights and user in weights:
                csv_weight = weights[user]
            csv2weights[file_path] = csv_weight
        return csv2weights

    def _multiprocess(self, params, num_threads, csv_files, csv2weights):
        # set up parallel processing
        manager = mp.Manager()
        writing_queue = manager.Queue()
        file_queue = manager.Queue()
        for fpath in csv_files:
            file_queue.put((fpath, csv2weights[fpath]))
        jobs = []

        # additional 1 process for writer
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool = mp.Pool(processes=num_threads + 1)
        signal.signal(signal.SIGINT, sigint_handler)
        try:
            collector_job = pool.apply_async(
                collector, (writing_queue, params, self.dev_mode))

            # Compute the density
            for _ in range(num_threads):
                jobs.append(pool.apply_async(mapper, (
                    writing_queue, params, file_queue, self.algorithm,
                    self.dev_mode, self.sandboxing)))

            # Clean up parallel processing (close pool, wait for processes to
            # finish, kill writing_queue, wait for queue to be killed)
            pool.close()
            for job in jobs:
                job.get()
            writing_queue.put('kill')  # stop collection
            result = collector_job.get()
            pool.join()
            return result
        except GracefulExit:
            pool.terminate()
            print("Exiting")
            pool.join()
            raise RuntimeError("Received interrupt signal, exiting. Bye.")

    def _singleprocess(self, params, csv_files, csv2weights):
        result_processor = ResultProcessor(params, self.dev_mode)
        jail = get_jail(python_version=2)
        for fpath in csv_files:
            scaler = csv2weights[fpath]
            result = process_user_csv(
                params, fpath, self.algorithm, self.dev_mode, self.sandboxing, jail)
            result_processor(result, scaler=scaler)
        return result_processor.get_result()
