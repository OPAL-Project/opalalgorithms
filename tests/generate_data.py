"""Generate data points.

python generate_data.py -c config
"""
from __future__ import division, print_function
import configargparse
from opalalgorithms.utils.datagenerator import OPALDataGenerator
import time
import multiprocessing as mp
import os
import math


parser = configargparse.ArgumentParser(
    description='Generate data for testing.')
parser.add_argument('-c', '--config', required=True, is_config_file=True,
                    help='Path to config file.')
parser.add_argument('--num_users', type=int, required=True,
                    help='Number of users to be created.')
parser.add_argument('--offset', type=int, required=True,
                    help='Offset to be used when creating users.')
parser.add_argument('--num_records_per_user', type=int, required=True,
                    help='Number of records to be created per user.')
parser.add_argument('--num_threads', type=int, required=True,
                    help='Number of threads to be used to create data.')
parser.add_argument('--num_antennas', type=int, required=True,
                    help='Total number of antennas available.')
parser.add_argument('--num_antennas_per_user', type=int, required=True,
                    help='Total number of antennas available per user.')
parser.add_argument('--data_path', required=True,
                    help='Data path where generated csv have to be saved.')
args = parser.parse_args()


#####################################
# main program                      #
#####################################


def generate(OPALDataGenerator, num_users, num_threads, offset=0):
    """Generate data for num_users mentioned.

    Args:
        OPALDataGenerator: Class Helper to generate the records
        num_users (int): Number of users to be created.
        offset (int): Offset for ID of users, by default ID starts from 1,
            if any offset is needed it can be set via this parameter.

    """
    step_size = int(math.ceil(num_users / num_threads))
    start_id_list = [j for j in range(offset, num_users+offset, step_size)]

    # set up parallel processing
    manager = mp.Manager()
    writing_queue = manager.Queue()
    jobs = []
    # additional 1 process is for which shouldn't take up much CPU power
    pool = mp.Pool(processes=num_threads + 1)
    pool.apply_async(write_user_to_csv, (writing_queue, args.data_path))

    # create the users
    print(start_id_list)
    for thread_id in range(num_threads):
        num_users_for_thread = min(
            num_users + offset - start_id_list[thread_id], step_size)
        jobs.append(pool.apply_async(
            generate_data, (
                writing_queue, thread_id, OPALDataGenerator, num_users_for_thread,
                start_id_list[thread_id])))

    # clean up parallel processing (close pool, wait for processes to
    # finish, kill writing_queue, wait for queue to be killed)
    pool.close()
    for job in jobs:
        job.get()
    writing_queue.put('kill')
    pool.join()


def write_user_to_csv(writing_queue, save_path):
    """Write user in writing_queue to csv."""
    while True:
        # wait for result to appear in the queue
        user = writing_queue.get()
        # if got signal 'kill' exit the loop
        if user == 'kill':
            break
        if(user is not None):
            csv_path = os.path.join(save_path, user[0] + '.csv')
            with open(csv_path, 'a') as csv:
                csv.write(user[1])
                csv.close()


def generate_data(writing_queue, threadID, OPALDataGenerator, num_users, start_id):
    """Generate data of the size required."""
    print("Starting " + str(threadID))
    start_time = time.time()
    print("Creating {} users, starting from id "
          "{}".format(num_users, start_id))
    for i in range(num_users):
        user = (str(start_id + i), OPALDataGenerator.generate_data())
        writing_queue.put(user)
    elapsed_time = time.time() - start_time
    print("The thread {} is done and it took: {}".format(
        threadID, elapsed_time))
    return "OK"


if __name__ == "__main__":
    # Prevent attempt to start a new process before the current process has finished its bootstrapping phase in Windows.
    if os.name == 'nt':
        mp.freeze_support()

    odg = OPALDataGenerator(args.num_antennas, args.num_antennas_per_user, args.num_records_per_user)
    generate(odg, args.num_users, args.num_threads, args.offset)
