import os
import time
from pathlib import Path
from typing import Set

from memory.interactive_policy import InteractivePolicyBase
from memory.entity import FileEntity
from memory.entity import VideoEntity
from memory.logger import g_logger
from memory.file_policy import FilePolicyBase
from memory.utils import walk_in_folder, timeit, is_ignored, make_unique_path, format_bytes, open_vlc


class MemoryStorage:
    def __init__(self, source_dir: Path,
                 target_dir: Path,
                 policy: FilePolicyBase,
                 interactive: InteractivePolicyBase,
                 ignore_dirs: Set[str] = None,
                 ignore_extentions: Set[str] = None,
                 whitelist_extentions: Set[str] = None,
                 ):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.policy: FilePolicyBase = policy
        self.interactive: InteractivePolicyBase = interactive

        if ignore_dirs:
            self.ignore_dirs = ignore_dirs
        else:
            self.ignore_dirs = set()

        if ignore_extentions:
            self.ignore_extentions = ignore_extentions
        else:
            self.ignore_extentions = set()

        if whitelist_extentions:
            self.whitelist_extentions = whitelist_extentions
        else:
            self.whitelist_extentions = set()

    @timeit
    def separate(self, path_pattern: str = '%Y/%m.%d'):
        g_logger.info('separate')

        for filepath in walk_in_folder(source_dir=self.source_dir, ignore_ext=self.ignore_extentions, ignore_dirs=self.ignore_dirs):
            if is_ignored(filepath, whitelist=self.whitelist_extentions):
                self.policy.blacklist_file(self.source_dir, filepath)
                continue

            entity = FileEntity(filepath)
            date = entity.get_original_date()

            if date is None:
                self.policy.failed_to_detected_original_date(self.source_dir, filepath)
                continue

            pattern = time.strftime(path_pattern, date.timetuple())
            dest_folder = self.target_dir.joinpath(pattern)
            dest_img_path = dest_folder.joinpath(entity.filename)

            is_duplicated = False
            while dest_img_path.exists():
                target_entity = FileEntity(dest_img_path)

                if entity.is_equal(target_entity):
                    is_duplicated = True
                    break

                dest_img_path = make_unique_path(dest_img_path)

            if is_duplicated:
                g_logger.warning("DUPLICATED: %s == %s", dest_img_path, filepath)
                self.policy.delete(self.source_dir, filepath)
            else:
                self.policy.move(filepath, dest_img_path)

    @timeit
    def remove_duplicated(self):
        g_logger.info('remove duplicated')

        size_duplication = {}
        for img_path in walk_in_folder(source_dir=self.source_dir, ignore_ext=self.ignore_extentions, ignore_dirs=self.ignore_dirs):
            entity = FileEntity(img_path)
            size_duplication.setdefault(entity.size, []).append(entity)

        duplicated_files = {}
        for duplicate_candidate in size_duplication.values():
            if len(duplicate_candidate) == 1:
                continue

            for entity in duplicate_candidate:
                duplicated_files.setdefault(entity.hexdigest, []).append(entity)

        for _, v in duplicated_files.items():
            if len(v) == 1:
                continue

            index = self.interactive.select_choice('> Choose file to keep', [str(f.filepath) for f in v])
            if index == -1:
                continue

            v.pop(index)

            for img in v:
                self.policy.delete(self.source_dir, img.filepath)

    @timeit
    def video_compress(self):
        g_logger.info('video compress')

        for f in walk_in_folder(source_dir=self.source_dir, ignore_ext=self.ignore_extentions, ignore_dirs=self.ignore_dirs):
            if not VideoEntity.is_video(f):
                continue

            # Move open action to policy
            open_vlc(f)

            choices = [
                video.get_original_resolution(),
                video.get_compressed_resolution(),
                'delete',
            ]
            index = self.interactive.select_choice(f'> Compress {video.filepath} size[{format_bytes(video.size)}]?', [str(c) for c in choices])

            if index == -1:
                continue

            if choices[index] == 'delete':
                self.policy.delete(self.source_dir, video.filepath)
                continue

            compressed_video = video.compress(choices[index])
            if video.size > compressed_video.size:
                g_logger.info('Keep compressed file')
                self.policy.delete(self.source_dir, video.filepath)
            else:
                g_logger.info('Original file is smaller, keep original')
                self.policy.delete(self.source_dir, compressed_video.filepath)

    @timeit
    def video_overview(self):
        g_logger.info('video overview')

        for f in walk_in_folder(source_dir=self.source_dir, ignore_ext=self.ignore_extentions, ignore_dirs=self.ignore_dirs):
            if not VideoEntity.is_video(f):
                continue

            # Move open action to policy
            open_vlc(f)

            video = VideoEntity(f)
            choices = [
                'keep',
                'delete',
            ]
            index = self.interactive.select_choice(f'> What to do {video.filepath} size[{format_bytes(video.size)}]?', choices)

            if index == -1:
                continue

            if choices[index] == 'delete':
                self.policy.delete(self.source_dir, video.filepath)
            else:
                continue
