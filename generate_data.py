"""Generate data points.

python generate_data.py -c config
"""
import random
import time
import string
import multiprocessing as mp
import configargparse
import os


__all__ = []
__author__ = 'Axel Oehmichen - ao1011@imparial.ac.uk'
__copyright__ = "Copyright 2017, Axel Oehmichen"
__credits__ = []
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Axel Oehmichen"
__email__ = "ao1011@imperial.ac.uk"
__status__ = "Dev"


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
parser.add_argument('--data_path', required=True,
                    help='Data path where generated csv have to be saved.')
args = parser.parse_args()


interactions = {
    0: "call",
    1: "text",
    2: "text",
    3: "text"
}

direction = {
    0: "in",
    1: "out"
}


def str_time_prop(start, end, format, prop):
    """Generate time as proportion between start time and end time."""
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    ptime = stime + prop * (etime - stime)
    return time.strftime(format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%Y-%m-%d %H:%M:%S', prop)


def users_generator(writing_queue, threadID, number_of_users_to_create,
                    number_of_records_per_user, id_number_start, offset,
                    number_of_antennas):
    print("Starting " + str(threadID))
    start_time = time.time()
    print(number_of_users_to_create, number_of_records_per_user,
          id_number_start)
    # users = set()
    for i in range(number_of_users_to_create):
        user = (
            str(id_number_start + i + offset), generate_random_lines(
                number_of_records_per_user, number_of_antennas))
        # users.add(user)
        writing_queue.put(user)
    elapsed_time = time.time() - start_time
    print("The thread %s is done and it took: %f" % (threadID, elapsed_time))

    return "OK"


def generate_random_lines(number_of_records_per_user, number_of_antennas):
    antennas = [str(random.randint(0, 1000)) for i in range(
        number_of_antennas)]
    users = [random.choice(string.ascii_letters) + random.choice(
        string.ascii_letters) for j in range(20)]
    lines = ''
    date = [random.random() for i in range(number_of_records_per_user)]
    date.sort()
    for k in range(number_of_records_per_user - 1):
        interaction = interactions[random.randint(0, 3)]
        line = interaction + ',' + direction[random.randint(0, 1)] + ',' + \
            users[random.randint(0, 19)] + ',' \
            + random_date("2016-01-01 00:00:01", "2016-12-31 23:59:59",
                          date[k]) + ','
        if interaction == "call":
            line += str(random.randint(0, 1000)) + ',' + antennas[
                random.randint(0, number_of_antennas - 1)]
        else:
            line += ',' + antennas[random.randint(0, number_of_antennas - 1)]
        lines += line + '\n'
    return lines


def users_writer(writing_queue):
    # keep writing into file data from queue
    while True:
        # wait for result to appear in the queue
        user = writing_queue.get()
        # if got signal 'kill' exit the loop
        if user == 'kill':
            break
        if(user is not None):
            csv_path = os.path.join(args.data_path, user[0] + '.csv')
            with open(csv_path, 'a') as csv:
                csv.write(user[1])
                csv.close()


def chunks(l, n):
    for i in range(0, l, n):
        yield i


#####################################
# main program                      #
#####################################

def main():
    number_of_users_to_create = args.num_users
    offset = args.offset
    # Number of records per day * one year
    number_of_records_per_user = args.num_records_per_user * 365
    number_of_threads = args.num_threads
    step = int(round(number_of_users_to_create / number_of_threads))
    c = chunks(number_of_users_to_create, step)
    chunks_list = list(c)
    number_of_antennas = 10

    # set up parallel processing
    manager = mp.Manager()
    writing_queue = manager.Queue()
    jobs = []
    # additional 1 process is for which shouldn't take up much CPU power
    pool = mp.Pool(
        processes=number_of_threads + 1)
    pool.apply_async(users_writer, (writing_queue,))

    # create the users
    i = 0
    for thread_id in range(number_of_threads):
        tot = step + chunks_list[i]
        if tot < number_of_users_to_create:
            jobs.append(pool.apply_async(
                users_generator, (writing_queue, thread_id, step,
                                  number_of_records_per_user, chunks_list[i],
                                  offset, number_of_antennas)))
        else:
            last_step = number_of_users_to_create - chunks_list[i]
            jobs.append(pool.apply_async(
                users_generator, (writing_queue, thread_id, last_step,
                                  number_of_records_per_user, chunks_list[i],
                                  offset, number_of_antennas)))
        i += 1

    # clean up parallel processing (close pool, wait for processes to finish,
    # kill writing_queue, wait for queue to be killed)
    pool.close()
    for job in jobs:
        job.get()
    writing_queue.put('kill')
    pool.join()


if __name__ == "__main__":
    main()
