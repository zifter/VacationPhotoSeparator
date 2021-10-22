import functools
import hashlib
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional

import exifread

# TODO add MOV file support

from memory.utils import make_new_name

DATE_TIME_ORIGINAL_PATTERN = "%Y:%m:%d %H:%M:%S"
DATE_TIME_ORIGINAL = 'DateTimeOriginal'
ALLOWED_EXIF_TAGS_ORDER = ['EXIF %s' % DATE_TIME_ORIGINAL, 'Image %s' % DATE_TIME_ORIGINAL]
ENCODED_DATE_IN_NAME_PATTERNS = [
    '%Y%m%d_%H%M%S',
    'IMG_%Y%m%d_%H%M%S',
    'IMG_%Y%m%d_%H%M%S_1',
    'VID_%Y%m%d_%H%M%S',
]


@functools.cache
def length(pattern: str) -> int:
    # get length of expected pattern
    return len(datetime.now().strftime(pattern))


def get_datetime_from_exif(file_path) -> Optional[datetime]:
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f, stop_tag=DATE_TIME_ORIGINAL, details=False)
        if not tags:
            return None

        for tag in ALLOWED_EXIF_TAGS_ORDER:
            if tag in tags:
                v = tags[tag].values
                try:
                    return datetime.strptime(v, DATE_TIME_ORIGINAL_PATTERN)
                except ValueError:
                    continue

    return None


def get_datetime_from_filename(file_name):
    for pattern in ENCODED_DATE_IN_NAME_PATTERNS:
        try:
            return datetime.strptime(file_name[0:length(pattern)], pattern)
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


class FileEntity:
    def __init__(self, filepath: Path):
        self.filepath: Path = filepath

    @property
    def filename(self) -> str:
        return self.filepath.name

    @property
    def size(self) -> int:
        return self.filepath.stat().st_size

    @property
    def hexdigest(self) -> str:
        m = hashlib.md5()
        with open(self.filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                m.update(chunk)

        return m.hexdigest()

    def is_equal(self, entity) -> bool:
        return self.size == entity.size and self.hexdigest == self.hexdigest

    def with_name(self, pattern: str):
        return make_new_name(self.filepath, pattern)

    def get_original_date(self) -> Optional[datetime]:
        file_stem = self.filepath.stem

        dates = [
            get_datetime_from_exif(self.filepath),
            get_datetime_from_filename(file_stem),
            get_creation_date(self.filepath),
        ]
        for d in dates:
            if d:
                return d

        return None
