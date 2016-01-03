import time
import shutil
import os
from argparse import ArgumentParser
import logging
from datetime import datetime

try:
    import exifread
except ImportError:
    # try to add exif-py to path
    from exif_py import exifread

DATE_TIME_ORIGINAL_PATTERN = "%Y:%m:%d %H:%M:%S"
DATE_TIME_ORIGINAL = 'DateTimeOriginal'
ALLOWED_EXIF_TAGS_ORDER = ['EXIF %s' % DATE_TIME_ORIGINAL, 'Image %s' % DATE_TIME_ORIGINAL]
ENCODED_DATE_IN_NAME_PATTERNS = ['%Y%m%d_%H%M%S']


def setup_logger(name):
    logger = logging.getLogger(name)
    stream = exifread.exif_log.Handler(logging.DEBUG, color=True)
    logger.addHandler(stream)
    return logger


g_logger = setup_logger('splitter')


class CopyFilePolicy():
    def __init__(self):
        pass

    @staticmethod
    def copy(src, dest):
        g_logger.info("Copy: %s -> %s" % (src, dest))
        shutil.copy(src, dest)

    @staticmethod
    def delete_duplicated(dest):
        pass


class MoveFilePolicy():
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


def get_original_date(imgPath):
    date = None
    # 1
    with open(imgPath, 'rb') as f:
        tags = exifread.process_file(f, stop_tag=DATE_TIME_ORIGINAL, details=False)
        for tag in ALLOWED_EXIF_TAGS_ORDER:
            if tag in tags:
                date = time.strptime(tags[tag].values, DATE_TIME_ORIGINAL_PATTERN)

    fileName = os.path.splitext(os.path.basename(imgPath))[0]
    for pattern in ENCODED_DATE_IN_NAME_PATTERNS:
        try:
            date = time.strptime(fileName, pattern)
        except ValueError:
            continue

    return date

    # 2
    # import PIL
    # from PIL import Image
    # from PIL.ExifTags import TAGS
    # img = PIL.Image.open(img_path)
    # exif_data = img._getexif()
    # for (k,v) in exif_data.iteritems():
    #     if TAGS.get(k) == 'DateTimeOriginal':
    #         date = time.strptime(v, DATE_TIME_ORIGINAL_PATTERN)


def split(context):
    for root, dirs, files in os.walk(context.source):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if not (context.extensions is None or ext in context.extensions):
                g_logger.debug('Skip: %s' % f)
                continue

            imgPath = os.path.join(root, f)
            date = get_original_date(imgPath)

            if date is None:
                g_logger.warning("Original Date did not detect: %s" % imgPath)
                continue

            destFolder = os.path.normpath(os.path.join(context.output, time.strftime(context.path_pattern, date)))
            destImgPath = os.path.join(destFolder, f)

            skipBecauseFilesEquals = False
            while os.path.exists(destImgPath):
                # files are equal?
                if os.stat(destImgPath).st_size == os.stat(imgPath).st_size and \
                                get_original_date(destImgPath) == date:
                    skipBecauseFilesEquals = True
                    break

                (name, ext) = os.path.splitext(destImgPath)
                destImgPath = "%s_DUPLICATE%s" % (name, ext)  # new name

            if skipBecauseFilesEquals:
                g_logger.warning("DUPLICATED: %s == %s" % (destImgPath, imgPath))
                try:
                    context.transfer_policy.delete_duplicated(imgPath)
                except Exception, e:
                    g_logger.error(e)
                continue

            if not os.path.exists(destFolder):
                os.makedirs(destFolder)

            try:
                context.transfer_policy.copy(imgPath, destImgPath)
            except Exception, e:
                g_logger.error(e)


def main():
    context = _get_execution_context()
    g_logger.setLevel(context.log_level.upper())

    g_logger.debug(context)

    startTime = datetime.now()
    g_logger.info("Start")
    split(context)
    g_logger.info("End [%s]" % (datetime.now() - startTime))


def _get_execution_context():
    argParser = ArgumentParser()
    argParser.add_argument('-s', '--source', required=True,
                           help="Source folder with files, which needs to be splitted.")
    argParser.add_argument('-o', '--output', required=True,
                           help="Output folder where splitted files will be.")

    argParser.add_argument('-m', '--move', dest='transfer_policy', action='store_const',
                           default=MoveFilePolicy(), const=MoveFilePolicy(),
                           help="Files will be moved from source folder into output folder. It's default value.")

    argParser.add_argument('-c', '--copy', dest='transfer_policy', action='store_const', const=CopyFilePolicy(),
                           help="Files will be copied into output folder.")

    argParser.add_argument('-l', '--log_level', dest='log_level', choices=['debug', 'info', 'warning', 'error'],
                           default='info', help="Log level for logger.")

    argParser.add_argument('-e', '--extensions', nargs='+', help="Log level for logger.")
    argParser.add_argument('-p', '--path_pattern', default='%Y/%m.%d', help="Pattern for output file path.")

    return argParser.parse_args()


if __name__ == "__main__":
    main()
