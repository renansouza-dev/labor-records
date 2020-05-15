from concurrent.futures.process import ProcessPoolExecutor

import GooglePhotos


def main():
    files = GooglePhotos.get_files()
    print('Downloaded {0} files.'.format(len(files)))
    Executor = ProcessPoolExecutor(max_workers=3)


if __name__ == '__main__':
    main()