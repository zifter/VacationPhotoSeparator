from functools import cached_property
from math import isclose, sqrt
from pathlib import Path
from typing import Dict, Tuple

import ffmpeg

from .file_entity import FileEntity


class VideoSettings:
    def __init__(self, info):
        self._info = info

    @cached_property
    def video_stream(self) -> Dict[str, str]:
        for stream in self._info['streams']:
            if stream['codec_type'] == 'video':
                return stream

        raise ValueError("failed to find video stream")

    @cached_property
    def resolution(self) -> Tuple[int, int]:
        return int(self.video_stream['width']), int(self.video_stream['height'])


class VideoEntity(FileEntity):
    EXTENSIONS = frozenset(['.mp4', '.avi', '.mp4', '.mpg', '.webp'])

    @staticmethod
    def is_video(filepath: Path):
        return filepath.suffix in VideoEntity.EXTENSIONS

    def __init__(self, filepath: Path):
        super(VideoEntity, self).__init__(filepath)

    @cached_property
    def settings(self) -> VideoSettings:
        return VideoSettings(ffmpeg.probe(self.filepath))

    def get_compressed_resolution(self) -> Tuple[int, int]:
        return self.get_target_resolution(self.settings.resolution)

    def get_original_resolution(self) -> Tuple[int, int]:
        return self.settings.resolution

    def compress(self, target_resolution, overwrite=False) -> 'VideoEntity':
        new_video_filename = self.with_name('{stem}_compressed{ext}')
        if new_video_filename.exists() and not overwrite:
            raise RuntimeError('Compressed file is already exists')

        input_stream = ffmpeg.input(self.filepath)
        args = {
            'vf': self.get_target_scale_arg(target_resolution, self.settings.resolution),
            'vcodec': 'libx265',
            'crf': 28,
        }

        ffmpeg.output(input_stream, str(new_video_filename.absolute()), **args).overwrite_output().run()
        return VideoEntity(new_video_filename)

    def get_target_resolution(self, current) -> Tuple[int, int]:
        target = [
            (1280, 720),
            (1024, 768),
            (720, 576),
        ]
        for t in target:
            if isclose(t[0]/t[1], current[0]/current[1]):
                return t

            if isclose(t[1]/t[0], current[0]/current[1]):
                return t[1], t[0]

        raise ValueError(f'failed to find target resolution {current}')

    def get_target_scale_arg(self, target, current) -> str:
        divider_sqrt = (current[0]*current[1])/(target[0]*target[1])

        divider = int(sqrt(divider_sqrt))
        return f'scale=trunc(iw/{divider*2})*2:trunc(ih/{divider*2})*2'
