import argparse
import logging
import os
from collections import defaultdict, namedtuple
from PIL import Image


def dhash(image, hash_size):
    # Grayscale and shrink the image.
    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

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

    return hash_num


def get_images(from_paths, file_types):
    for path in from_paths:
        for root, dirs, files in os.walk(path):
            for name in files:
                file_path = os.path.join(root, name)
                if (file_path.endswith(file_types)):
                    yield file_path


parser = argparse.ArgumentParser()
parser.add_argument('paths', nargs='+', help='Find images from')
parser.add_argument('-S', '--hashsize', type=int, default=8,
                    help='Hash size.'
                    ' give greater number for more finely search')
parser.add_argument('-v', '--verbose', default=0, action='count',
                    help='Verbose output')
parser.add_argument('-s', '--simulate', action='store_true',
                    help='simulate mode. It does not remove image files')

ImageFile = namedtuple('ImageFile', ('path', 'size'))


def remove_images(path, hash_size=8, simulate=False):
    img_paths = get_images(path, ('.png', '.jpg'))
    imgs = defaultdict(list)
    for img_path in img_paths:
        try:
            logging.debug(img_path)
            image = Image.open(img_path)
            size = image.size[0] * image.size[1]
            img_hash = dhash(image, hash_size)
            imgs[img_hash].append(ImageFile(img_path, size))
        except IOError as e:
            logging.warning('{}: {}', img_path, e)
            continue

    count = 0
    for images in imgs.values():
        if len(images) < 2:
            continue

        best_image = max(images, key=lambda x: (
            x.size, os.path.getsize(x.path), os.path.getmtime(x.path)))
        logging.info('leaving best image: {0}'.format(best_image.path))
        for image in images:
            if image != best_image:
                logging.info('Removing: {0}'.format(image.path))
                count += 1
                if not simulate:
                    os.remove(image.path)

    logging.info('Removed {0} images.'.format(count))


def main():
    args = parser.parse_args()

    log_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = 1 if args.simulate else 0
    log_level += args.verbose
    try:
        logging_level = log_levels[log_level]
    except IndexError:
        logging_level = log_levels[-1]

    logging.basicConfig(format='%(message)s', level=logging_level)
    remove_images(args.paths, args.hashsize, args.simulate)


if __name__ == '__main__':
    main()
