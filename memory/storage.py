import time
from pathlib import Path
from typing import Set

from .interactive_policy import InteractivePolicyBase
from .entity import Entity
from .logger import g_logger
from .file_policy import FilePolicyBase
from .utils import walk_in_folder, timeit, is_ignored, make_unique_path


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

            entity = Entity(filepath)
            date = entity.get_original_date()

            if date is None:
                self.policy.failed_to_detected_original_date(self.source_dir, filepath)
                continue

            pattern = time.strftime(path_pattern, date.timetuple())
            dest_folder = self.target_dir.joinpath(pattern)
            dest_img_path = dest_folder.joinpath(entity.filename)

            is_duplicated = False
            while dest_img_path.exists():
                target_entity = Entity(dest_img_path)

                if entity.is_equal(target_entity):
                    is_duplicated = True
                    break

                dest_img_path = make_unique_path(dest_img_path)

            if is_duplicated:
                g_logger.warning("DUPLICATED: %s == %s" % (dest_img_path, filepath))
                self.policy.delete(self.source_dir, filepath)
            else:
                self.policy.move(filepath, dest_img_path)

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

            index = self.interactive.choose_to_keep([f.filepath for f in v])
            v.pop(index)

            to_remove.extend(v)

        g_logger.debug('duplicated files count', len(to_remove))
        g_logger.debug(to_remove)
        for img in to_remove:
            self.policy.delete(self.source_dir, img.filepath)
