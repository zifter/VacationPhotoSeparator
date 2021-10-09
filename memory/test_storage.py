import tempfile
from pathlib import Path

from paths import TEST_DATA_DIR
from policy import DebugFilePolicy
from storage import MemoryStorage

TEST_SOURCE_DIR = TEST_DATA_DIR.joinpath('test_source')


def test_storage_separate():
    storage = MemoryStorage(TEST_SOURCE_DIR, Path(tempfile.mkdtemp()), DebugFilePolicy())
    storage.separate('%Y/%m.%d')


def test_storage_remove_duplicated():
    storage = MemoryStorage(TEST_SOURCE_DIR, Path(tempfile.mkdtemp()), DebugFilePolicy())
    storage.remove_duplicated()
