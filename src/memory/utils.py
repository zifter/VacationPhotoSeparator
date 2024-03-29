import os
from pathlib import Path
from typing import Iterator, Set

from functools import wraps
from time import time

from .logger import g_logger


def walk_in_folder(source_dir: Path, ignore_ext: Set[str] = None, ignore_dirs: Set[str] = None) -> Iterator[Path]:
    if not ignore_ext:
        ignore_ext = set()
    if not ignore_dirs:
        ignore_dirs = set()

    assert all([ext.startswith('.') for ext in ignore_ext]), f"ext must be provided with dot - {ignore_ext}"

    for root, dirs, files in os.walk(source_dir):
        r = Path(root)
        if r.name in ignore_dirs:
            continue

        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in ignore_ext:
                g_logger.debug('Skip: %s' % f)
                continue

            yield r.joinpath(f)


def timeit(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        g_logger.info('%r took: %2.4f sec', f.__name__, te-ts)
        return result

    return wrap


def make_unique_path(path: Path):
    i = 0
    while path.exists():
        path = path.with_name(path.stem + f'_duplicated_{i}' + path.suffix)
        i += 1

    return path


def make_new_name(path: Path, pattern: str) -> Path:
    pattern = pattern.format(stem=path.stem, ext=path.suffix)
    return path.with_name(pattern)


def is_ignored(path: Path, whitelist: Set[str]) -> bool:
    return path.suffix.lower() not in whitelist


def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n]+'bytes'


def open_vlc(filepath: Path):
    os.system(f'vlc "{filepath}"')
