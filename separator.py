import os
import platform
import time
import shutil
import logging
from argparse import ArgumentParser
from datetime import datetime
import hashlib

import exifread

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

    return get_datetime_from_exif(file_path) \
           or get_datetime_from_filename(file_name) \
           or get_creation_date(file_path)


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


def get_creation_date(file_path):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        timestamp = min(os.path.getctime(file_path), os.path.getmtime(file_path))
    else:
        stat = os.stat(file_path)
        try:
            timestamp = stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            timestamp = stat.st_mtime

    if timestamp is not None:
        return datetime.fromtimestamp(timestamp)

    return None


def walk_in_source(context):
    for root, dirs, files in os.walk(context.source):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if context.extensions is not None and ext in context.extensions:
                g_logger.debug('Skip: %s' % f)
                continue

            img_path = os.path.join(root, f)
            yield img_path


def separate(context):
    for img_path in walk_in_source(context):
        date = get_original_date(img_path)

        if date is None:
            g_logger.warning("Original Date did not detect: %s" % img_path)
            continue

        dest_folder = os.path.normpath(
            os.path.join(context.output, time.strftime(context.path_pattern, date.timetuple())))
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


def remove_duplicated(context):
    duplicated_sizes = {}
    for img_path in walk_in_source(context):
        duplicated_sizes.setdefault(os.stat(img_path).st_size, []).append(img_path)

    duplicated_files = {}
    for duplicate_candidate in duplicated_sizes.values():
        if len(duplicate_candidate) > 1:
            for candidate in duplicate_candidate:
                m = hashlib.md5()
                with open(candidate, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        m.update(chunk)

                duplicated_files.setdefault(m.hexdigest(), []).append(candidate)

    for k, v in duplicated_files.items():
        if len(v) > 1:
            to_remove = v[1:]
            g_logger.info(to_remove)

            dest = os.path.join(context.output, os.path.relpath(v[0], context.source))
            dest_folder = os.path.abspath(os.path.join(dest, os.pardir))
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            g_logger.info('Copy {} to {}'.format(v[0], dest))
            shutil.copy(v[0], dest)
            for img in to_remove:
                g_logger.info('Remove {}'.format(img))
                # os.remove(img)


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
    context.action(context)
    g_logger.info(" - [End %s]" % (datetime.now() - start_time))


def _get_execution_context():
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-sep', '--separate', dest='action',  action='store_const', const=separate, default=separate,
                            help="Separate files by dates.")
    arg_parser.add_argument('-rem', '--remove_duplicated', dest='action',  action='store_const', const=remove_duplicated,
                            help="Remove duplicated files")
    arg_parser.add_argument('-s', '--source', required=True,
                            help="Source folder with files, which needs to be split.")
    arg_parser.add_argument('-o', '--output', default=None,
                            help="Output folder where split files will be. By default will be place near source folder.")

    arg_parser.add_argument('-m', '--move', dest='transfer_policy', action='store_const',
                            default=MoveFilePolicy(), const=MoveFilePolicy(),
                            help="Files will be moved from source folder into output folder. It's default value.")

    arg_parser.add_argument('-c', '--copy', dest='transfer_policy', action='store_const', const=CopyFilePolicy(),
                            help="Files will be copied into output folder.")

    arg_parser.add_argument('-l', '--log_level', dest='log_level', choices=['debug', 'info', 'warning', 'error'],
                            default='info', help="Log level for logger.")

    arg_parser.add_argument('-ext', '--extensions', nargs='+', help="Ignore file extensions.")
    arg_parser.add_argument('-p', '--path_pattern', default='%Y/%m.%d', help="Pattern for output file path.")

    return arg_parser.parse_args()


if __name__ == "__main__":
    main()
