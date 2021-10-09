import os
import time
from pathlib import Path
from typing import Set

from .entity import Entity
from .logger import g_logger
from .policy import FilePolicyBase
from .utils import walk_in_folder, timeit


class MemoryStorage:
    def __init__(self, source_dir: Path, target_dir: Path, policy: FilePolicyBase, ignore_dirs: Set[str]=None):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.ignore_dirs = ignore_dirs
        self.policy = policy
        self.ignore_extentions = set()

    @timeit
    def separate(self, path_pattern: str = '%Y/%m.%d'):
        g_logger.info('separate')

        for img_path in walk_in_folder(source_dir=self.source_dir, ignore_ext=self.ignore_extentions, ignore_dirs=self.ignore_dirs):
            entity = Entity(img_path)
            date = entity.get_original_date()

            if date is None:
                g_logger.warning("Original Date did not detect: %s" % img_path)
                continue

            pattern = time.strftime(path_pattern, date.timetuple())
            dest_folder = self.target_dir.joinpath(pattern)
            dest_img_path = dest_folder.joinpath(entity.filename)

            is_duplicated = False
            while os.path.exists(dest_img_path):
                target_entity = Entity(dest_img_path)

                if entity.is_equal(target_entity):
                    is_duplicated = True
                    break

                (name, ext) = os.path.splitext(dest_img_path)
                dest_img_path = "%s_DUPLICATE%s" % (name, ext)  # new name

            if is_duplicated:
                g_logger.warning("DUPLICATED: %s == %s" % (dest_img_path, img_path))
                self.policy.delete(self.source_dir, img_path)
            else:
                self.policy.move(img_path, dest_img_path)

    @timeit
    def remove_duplicated(self):
        g_logger.info('remove duplicated')

        size_duplication = {}
        for img_path in walk_in_folder(source_dir=self.source_dir, ignore_ext=self.ignore_extentions, ignore_dirs=self.ignore_dirs):
            entity = Entity(img_path)
            size_duplication.setdefault(entity.size, []).append(entity)

        duplicated_files = {}
        for duplicate_candidate in size_duplication.values():
            if len(duplicate_candidate) == 1:
                continue

            for entity in duplicate_candidate:
                duplicated_files.setdefault(entity.hexdigest, []).append(entity)

        to_remove = []
        for k, v in duplicated_files.items():
            if len(v) == 1:
                continue

            to_remove.extend(v[1:])

        g_logger.debug('duplicated files count', len(to_remove))
        g_logger.debug(to_remove)
        for img in to_remove:
            self.policy.delete(self.source_dir, img.filepath)
