from datetime import datetime
from parameterized import parameterized

from .file_entity import get_datetime_from_filename, FileEntity
from memory.paths import TEST_DATA_DIR

TEST_FILE = 'test_file.jpg'
entity = FileEntity(TEST_DATA_DIR.joinpath('entity').joinpath(TEST_FILE))

TEST_FILE2 = 'test_file2.jpg'
entity2 = FileEntity(TEST_DATA_DIR.joinpath('entity').joinpath(TEST_FILE2))


@parameterized.expand([
    ('20180213_094124', datetime(year=2018, month=2, day=13, hour=9, minute=41, second=24)),
    ('VID_20190213_094124', datetime(year=2019, month=2, day=13, hour=9, minute=41, second=24)),
    ('VID_20190105_123419', datetime(year=2019, month=1, day=5, hour=12, minute=34, second=19)),
    ('IMG_20191013_091101', datetime(year=2019, month=10, day=13, hour=9, minute=11, second=1)),
    ('IMG_20191210_115330_1', datetime(year=2019, month=12, day=10, hour=11, minute=53, second=30)),
    ('IMG_20191210_115330_compressed', datetime(year=2019, month=12, day=10, hour=11, minute=53, second=30)),
])
def test_detect_from_base(filename, datetime_stamp):
    assert get_datetime_from_filename(filename) == datetime_stamp


def test_entity_filename():
    assert entity.filename == TEST_FILE


def test_entity_size():
    assert entity.size == 47801


def test_entity_hexdigest():
    assert entity.hexdigest == '7363261bdf4d1ee08c746e93ca3c3695'


def test_entity_is_equal():
    assert entity.is_equal(entity)
    assert not entity.is_equal(entity2)
