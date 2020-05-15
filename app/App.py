import datetime
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

from app import GooglePhotos


def print_metadata(file):
    return datetime.datetime.strptime(file['creationTime'], '%Y-%m-%dT%H:%M:%S%z')


def main():
    start = time.process_time()

    newest_file = None
    pool = ThreadPoolExecutor(max_workers=os.cpu_count())
    for future in as_completed([pool.submit(print_metadata, file) for file in GooglePhotos.get_files()]):
        if newest_file is None or future.result() > newest_file:
            newest_file = future.result()

    elapsed = timedelta(seconds=time.process_time()-start)
    print('Printed all metadata from files in {0} and the newest is from {1}.'.format(elapsed, newest_file))


if __name__ == '__main__':
    main()