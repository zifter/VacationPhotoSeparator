import os
from pathlib import Path

from memory.video_entity import VideoEntity
from memory.paths import TEST_DATA_DIR

TEST_FILE = 'VID_20210627_134101.mp4'
video_entity = VideoEntity(TEST_DATA_DIR.joinpath('video').joinpath(TEST_FILE))


def test_check_ext():
    assert VideoEntity.is_video(Path('video.mp4')) is True


def test_compress_video():
    original_date = video_entity.get_original_date()

    new_video = video_entity.compress(overwrite=True)

    assert new_video.filepath.exists() is True
    assert original_date == new_video.get_original_date()

    os.remove(new_video.filepath)
