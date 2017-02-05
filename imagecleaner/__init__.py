import argparse
import functools
import hashlib
import logging
import os

from collections import defaultdict, namedtuple
from multiprocessing import Pool, cpu_count
from os import path

import appdirs
from PIL import Image

try:
    xrange
except NameError:
    xrange = range

caching_dir = appdirs.user_cache_dir('imagecleaner', 'kjwon15')
if not path.exists(caching_dir):
    os.mkdir(caching_dir)

logger = logging.getLogger(__name__)


def dhash(image, hash_size):
    # Grayscale and shrink the image.
    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

    try:
        cache_name = path.join(
            caching_dir,
            hashlib.sha256(image.tobytes()).hexdigest()
        )
        with open(cache_name) as fp:
            hash_num = int(fp.read())
            logger.debug('Using cache')
    except (IOError, ValueError):
        differences = []
        for row in xrange(hash_size):
            for col in xrange(hash_size):
                pixel_left = image.getpixel((col, row))
                pixel_right = image.getpixel((col + 1, row))

                differences.append(pixel_left > pixel_right)

        hash_num = 0
        for value in differences:
            hash_num *= 2
            if value:
                hash_num += 1

        with open(cache_name, 'w') as fp:
            fp.write(str(hash_num))

    return hash_num


def get_images(from_paths, file_types):
    for path_ in from_paths:
        for root, dirs, files in os.walk(path_):
            for name in files:
                file_path = os.path.join(root, name)
                if (file_path.endswith(file_types)):
                    yield file_path


parser = argparse.ArgumentParser()
parser.add_argument('paths', nargs='+', help='Find images from')
parser.add_argument('-S', '--hashsize', type=int, default=16,
                    help='Hash size.'
                    ' give greater number for more finely search')
parser.add_argument('-v', '--verbose', default=0, action='count',
                    help='Verbose output')
parser.add_argument('-s', '--simulate', action='store_true',
                    help='simulate mode. It does not remove image files')
parser.add_argument(
    '-t', '--threads', type=int, default=0,
    help="Thread counts, negative value means -value * cpu_count")

ImageFile = namedtuple('ImageFile', ('path', 'size'))


def get_image_hash(hash_size, img_path):
    try:
        logger.debug(img_path)
        image = Image.open(img_path)
        size = image.size[0] * image.size[1]
        img_hash = dhash(image, hash_size)
        return (img_hash, ImageFile(img_path, size))
    except IOError as e:
        logger.warning('{}: {}', img_path, str(e))


def remove_images(path, hash_size, threads_count, simulate=False):
    img_paths = get_images(path, ('.png', '.jpg'))
    imgs = defaultdict(list)
    get_image_partial = functools.partial(get_image_hash, hash_size)

    try:
        if threads_count < 0:
            threads_count = -threads_count * cpu_count()
        elif threads_count == 0:
            # Failsafe
            threads_count = cpu_count()
        logger.debug('Using {} threads'.format(threads_count))
        pool = Pool(threads_count)
        for result in pool.map(get_image_partial, img_paths):
            if result is None:
                continue
            img_hash, img_file = result
            imgs[img_hash].append(img_file)

    except KeyboardInterrupt:
        pool.terminate()
    else:
        pool.close()
    finally:
        pool.join()

    count = 0
    for images in imgs.values():
        if len(images) < 2:
            continue

        best_image = max(images, key=lambda x: (
            x.size, os.path.getsize(x.path), os.path.getmtime(x.path)))
        logger.info('leaving best image: {0}'.format(best_image.path))
        for image in images:
            if image != best_image:
                logger.info('Removing: {0}'.format(image.path))
                count += 1
                if not simulate:
                    os.remove(image.path)

    logger.info('Removed {0} images.'.format(count))


def main():
    args = parser.parse_args()

    log_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = 1 if args.simulate else 0
    log_level += args.verbose
    try:
        logging_level = log_levels[log_level]
    except IndexError:
        logging_level = log_levels[-1]

    logging.basicConfig(format='%(message)s')
    logger.setLevel(logging_level)
    remove_images(args.paths, args.hashsize, args.threads, args.simulate)


if __name__ == '__main__':
    main()
