import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

from app import GooglePhotos


def print_metadata(file):
    return file['creationTime']


def main():
    start = time.process_time()

    last_processed = None
    if os.path.exists('resources/last_processed.txt'):
        with open('resources/last_processed.txt', 'r') as last:
            last_processed = last.read()

    pool = ThreadPoolExecutor(max_workers=os.cpu_count())
    for future in as_completed([pool.submit(print_metadata, file) for file in GooglePhotos.get_files(last_processed)]):
        if last_processed is None or future.result() > last_processed:
            last_processed = future.result()

    if last_processed is not None:
        last_processed_file = open('resources/last_processed.txt', 'w+')
        last_processed_file.write(last_processed)
        last_processed_file.close()

    elapsed = timedelta(seconds=time.process_time()-start)
    print('Processed all files in {0} and the last processed is from {1}.'.format(elapsed, last_processed))


if __name__ == '__main__':
    main()