import unittest

from datetime import datetime
from parameterized import parameterized
from separator import get_datetime_from_filename


class SourceFilenameTestCase(unittest.TestCase):
    @parameterized.expand([
        ('20180213_094124', datetime(year=2018, month=2, day=13, hour=9, minute=41, second=24)),
        ('VID_20190213_094124', datetime(year=2019, month=2, day=13, hour=9, minute=41, second=24)),
        ('VID_20190105_123419', datetime(year=2019, month=1, day=5, hour=12, minute=34, second=19)),
        ('IMG_20191013_091101', datetime(year=2019, month=10, day=13, hour=9, minute=11, second=1)),
        ('IMG_20191210_115330_1', datetime(year=2019, month=12, day=10, hour=11, minute=53, second=30)),
    ])
    def test_detect_from_base(self, filename, datetime_stamp):
        self.assertEqual(get_datetime_from_filename(filename), datetime_stamp)
