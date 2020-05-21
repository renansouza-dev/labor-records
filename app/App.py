import os
import time
import urllib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

import cv2
import pytesseract
from PIL import Image

from app import GooglePhotos


def print_metadata(file):
    urllib.request.urlretrieve(file['url'], file['filename'])

    # load the example image and convert it to grayscale
    image = cv2.imread(file['filename'])
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # check to see if we should apply thresholding to preprocess the
    # image
    # if args["preprocess"] == "thresh":
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # make a check to see if median blurring should be done to remove
    # noise
    # elif args["preprocess"] == "blur":
    gray = cv2.medianBlur(gray, 3)
    # write the grayscale image to disk as a temporary file so we can
    # apply OCR to it
    filename = "{}.png".format(file['filename'])
    cv2.imwrite(filename, gray)

    image_text1 = pytesseract.image_to_string(Image.open(file['filename']), lang='por')
    text_file = open(file['filename'] + '1.txt', 'w+')
    text_file.write(image_text1)
    text_file.close()

    image_text2 = pytesseract.image_to_string(Image.open(filename), lang='por')
    text_file = open(file['filename'] + '2.txt', 'w+')
    text_file.write(image_text2)
    text_file.close()

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