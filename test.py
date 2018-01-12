"""Test population density algorithm."""
import sys
import time
import os
import multiprocessing as mp


def mapper(writing_queue, users_csv_files, algorithmobj):
    """Map user_data to result."""
    for user_csv_file in users_csv_files:
        username = os.path.splitext(os.path.basename(user_csv_file))[0]
        result = algorithmobj.map(user_csv_file)
        writing_queue.put((username, result))


def collector(writing_queue, results_csv_path):
    """Collect the results in writing queue in a single csv."""
    with open(results_csv_path, 'a') as csv:
        while True:
            # wait for result to appear in the queue
            user = writing_queue.get()
            # if got signal 'kill' exit the loop
            if user == 'kill':
                break
            if user is not None:
                csv.write(user[0] + ' ' + user[1] + '\n')
        csv.close()


def reducer(algorithmobj, results_csv_path):
    """Reduce the results from a csv to a single number."""
    return algorithmobj.reduce(results_csv_path)


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def main():
    """Main function."""
    # load the algorithm
    mod = __import__('opalalgorithms', fromlist=['PopulationDensity'])
    algorithmclass = getattr(mod, 'PopulationDensity')
    algorithmobj = algorithmclass()

    results_csv_path = 'results/results.csv'

    start_time = time.time()
    data_dir = str(sys.argv[1])
    number_of_threads = int(sys.argv[2])
    csvfiles = [os.path.join(
        os.path.abspath(data_dir), f) for f in os.listdir(data_dir)]
    step = int(round(len(csvfiles) / number_of_threads))
    c = chunks(csvfiles, step)

    # set up parallel processing
    manager = mp.Manager()
    writing_queue = manager.Queue()
    jobs = []

    # additional 1 process for writer
    pool = mp.Pool(processes=number_of_threads + 1)
    pool.apply_async(collector, (writing_queue, results_csv_path,))

    # Compute the density
    i = 0
    chunks_list = list(c)
    for thread_id in range(number_of_threads):
        mapper(writing_queue, chunks_list[i], algorithmobj)
        # jobs.append(pool.apply_async(mapper, (
        #     writing_queue, chunks_list[i], algorithmobj)))
        i += 1

    # Clean up parallel processing (close pool, wait for processes to finish,
    # kill writing_queue, wait for queue to be killed)
    pool.close()
    for job in jobs:
        print(job)
        job.get()
    writing_queue.put('kill')
    pool.join()
    print("Population density : {}".format(
        reducer(algorithmobj, results_csv_path)))
    elapsed_time = time.time() - start_time
    print("The density computation is done and it took: %f" % elapsed_time)


if __name__ == "__main__":
    main()
