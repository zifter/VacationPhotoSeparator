import os
from pathlib import Path

import ffmpeg

from memory.file_entity import FileEntity


class VideoEntity(FileEntity):
    EXTENSIONS = frozenset(['.mp4', '.avi', '.mp4', '.mpg', '.webp'])

    @staticmethod
    def is_video(filepath: Path):
        return filepath.suffix in VideoEntity.EXTENSIONS

    def __init__(self, filepath: Path):
        super(VideoEntity, self).__init__(filepath)

    def compress(self, overwrite=False) -> 'VideoEntity':
        new_video_filename = self.with_name('{stem}_compressed{ext}')
        if new_video_filename.exists() and not overwrite:
            raise RuntimeError('Compressed file is already exists')

        input_stream = ffmpeg.input(self.filepath)

        result = ffmpeg.probe(self.filepath)
        settings = {
            'vf': "scale=trunc(iw/6)*2:trunc(ih/6)*2",
            'vcodec': 'libx265',
            'crf': 28,
        }

        ffmpeg.output(input_stream, str(new_video_filename.absolute()), **settings).overwrite_output().run()
        return VideoEntity(new_video_filename)
