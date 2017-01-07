import time
import shutil
import os
import exifread
import logging
from argparse import ArgumentParser
from datetime import datetime


# TODO add MOV file support

DATE_TIME_ORIGINAL_PATTERN = "%Y:%m:%d %H:%M:%S"
DATE_TIME_ORIGINAL = 'DateTimeOriginal'
ALLOWED_EXIF_TAGS_ORDER = ['EXIF %s' % DATE_TIME_ORIGINAL, 'Image %s' % DATE_TIME_ORIGINAL]
ENCODED_DATE_IN_NAME_PATTERNS = [
    '%Y%m%d_%H%M%S',
    'IMG_%Y%m%d_%H%M%S',
    'IMG_%Y%m%d_%H%M%S_1',
    'VID_%Y%m%d_%H%M%S',
]


def setup_logger(name):
    logger = logging.getLogger(name)
    stream = logging.StreamHandler()
    logger.addHandler(stream)
    return logger


g_logger = setup_logger('separator')


class CopyFilePolicy(object):
    def __init__(self):
        pass

    @staticmethod
    def copy(src, dest):
        g_logger.info("Copy: %s -> %s" % (src, dest))
        shutil.copy(src, dest)

    @staticmethod
    def delete_duplicated(dest):
        pass


class MoveFilePolicy(object):
    def __init__(self):
        pass

    @staticmethod
    def copy(src, dest):
        g_logger.info("Move: %s -> %s" % (src, dest))
        shutil.move(src, dest)

    @staticmethod
    def delete_duplicated(dest):
        g_logger.info("Remove duplicated: %s" % dest)
        os.remove(dest)


def get_original_date(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    return get_datetime_from_exif(file_path) or get_datetime_from_filename(file_name)


def get_datetime_from_exif(file_path):
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f, stop_tag=DATE_TIME_ORIGINAL, details=False)
        for tag in ALLOWED_EXIF_TAGS_ORDER:
            if tag in tags:
                v = tags[tag].values
                try:
                    return datetime.strptime(v, DATE_TIME_ORIGINAL_PATTERN)
                except ValueError:
                    continue


def get_datetime_from_filename(file_name):
    for pattern in ENCODED_DATE_IN_NAME_PATTERNS:
        try:
            return datetime.strptime(file_name, pattern)
        except ValueError:
            continue

    return None


def separate(context):
    for root, dirs, files in os.walk(context.source):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if not (context.ingore_extensions is None or ext in context.ingore_extensions):
                g_logger.debug('Skip: %s' % f)
                continue

            img_path = os.path.join(root, f)
            date = get_original_date(img_path)

            if date is None:
                g_logger.warning("Original Date did not detect: %s" % img_path)
                continue

            dest_folder = os.path.normpath(os.path.join(context.output, time.strftime(context.path_pattern, date.timetuple())))
            dest_img_path = os.path.join(dest_folder, f)

            skip_because_files_equals = False
            while os.path.exists(dest_img_path):
                # files are equal?
                if os.stat(dest_img_path).st_size == os.stat(img_path).st_size and \
                                get_original_date(dest_img_path) == date:
                    skip_because_files_equals = True
                    break

                (name, ext) = os.path.splitext(dest_img_path)
                dest_img_path = "%s_DUPLICATE%s" % (name, ext)  # new name

            if skip_because_files_equals:
                g_logger.warning("DUPLICATED: %s == %s" % (dest_img_path, img_path))
                try:
                    context.transfer_policy.delete_duplicated(img_path)
                except Exception as e:
                    g_logger.error(e)
                continue

            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            try:
                context.transfer_policy.copy(img_path, dest_img_path)
            except Exception as e:
                g_logger.error(e)


def main():
    context = _get_execution_context()
    if context.output is None:
        assert context.source is not None

        source_dirname = os.path.dirname(context.source)
        context.output = os.path.normpath(os.path.join(context.source, '..', '{}_sorted'.format(source_dirname)))

    g_logger.setLevel(context.log_level.upper())

    g_logger.debug(context)

    start_time = datetime.now()
    g_logger.info(" - [Start]")
    separate(context)
    g_logger.info(" - [End %s]" % (datetime.now() - start_time))


def _get_execution_context():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-s', '--source', required=True,
                           help="Source folder with files, which needs to be splitted.")
    arg_parser.add_argument('-o', '--output', default=None,
                           help="Output folder where splitted files will be. By default will be place near source folder.")

    arg_parser.add_argument('-m', '--move', dest='transfer_policy', action='store_const',
                           default=MoveFilePolicy(), const=MoveFilePolicy(),
                           help="Files will be moved from source folder into output folder. It's default value.")

    arg_parser.add_argument('-c', '--copy', dest='transfer_policy', action='store_const', const=CopyFilePolicy(),
                           help="Files will be copied into output folder.")

    arg_parser.add_argument('-l', '--log_level', dest='log_level', choices=['debug', 'info', 'warning', 'error'],
                           default='info', help="Log level for logger.")

    arg_parser.add_argument('-e', '--ingore_extensions', nargs='+', help="Ignore file extensions.")
    arg_parser.add_argument('-p', '--path_pattern', default='%Y/%m.%d', help="Pattern for output file path.")

    return arg_parser.parse_args()


if __name__ == "__main__":
    main()
