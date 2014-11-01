import argparse
import logging
import os
from collections import namedtuple
from PIL import Image

__version__ = '0.2.0'


def dhash(image, hash_size=8):
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


def get_images(from_path, file_types):
    for root, dirs, files in os.walk(from_path):
        for name in files:
            file_path = os.path.join(root, name)
            if (file_path.endswith(file_types)):
                yield file_path


parser = argparse.ArgumentParser()
parser.add_argument('path', help='Find images from')
parser.add_argument('-v', '--verbose', default=0, action='count',
                    help='Verbose output')
parser.add_argument('-s', '--simulate', action='store_true')

ImageFile = namedtuple('ImageFile', ('path', 'size'))


def remove_images(path, simulate=False):
    img_paths = get_images(path, ('.png', '.jpg'))
    imgs = {}
    for img_path in img_paths:
        try:
            image = Image.open(img_path)
            size = image.size[0] * image.size[1]
            img_hash = dhash(image)
            if img_hash not in imgs:
                imgs[img_hash] = []
            imgs[img_hash].append(ImageFile(img_path, size))
        except IOError as e:
            logging.warning(e.message)
            continue

    duplicated = dict((key, imgs[key]) for key in imgs if len(imgs[key]) > 1)

    for images in duplicated.values():
        best_image = max(images, key=lambda x: x.size)
        for image in images:
            if image != best_image:
                logging.info('Removing: {0}'.format(image.path))
                if not simulate:
                    os.remove(image.path)


def main():
    args = parser.parse_args()

    log_level = logging.WARNING
    if args.verbose or args.simulate:
        log_level = logging.INFO

    logging.basicConfig(format='%(message)s', level=log_level)
    remove_images(args.path, args.simulate)


if __name__ == '__main__':
    main()
