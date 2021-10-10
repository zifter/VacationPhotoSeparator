import shutil
from pathlib import Path

from overrides import overrides

from ..utils import make_unique_path
from ..logger import g_logger
from .base import FilePolicyBase


class SafeFilePolicy(FilePolicyBase):
    def __init__(self, safe_dir: Path):
        super().__init__()

        self.safe_dir = safe_dir

    def _move_to_safe_zone(self, zone_name: str, source_dir: Path, dest: Path):
        relative = dest.relative_to(source_dir)

        move_to = self.safe_dir.joinpath(zone_name).joinpath(relative)

        if not move_to.parent.exists():
            move_to.parent.mkdir(parents=True)

        move_to = make_unique_path(move_to)

        g_logger.info("move: %s -> %s" % (dest, dest))
        shutil.move(dest, move_to)

    @overrides
    def failed_to_detected_original_date(self, source_dir: Path, src: Path):
        g_logger.info("failed to detect, move to safe zone: %s" % src)

        self._move_to_safe_zone('failed', source_dir, src)

    @overrides
    def blacklist_file(self, source_dir: Path, src: Path):
        g_logger.info("ignore file: %s" % src)

        self._move_to_safe_zone('ignored', source_dir, src)

    @overrides
    def move(self, src: Path, dest: Path):
        g_logger.info("move: %s -> %s" % (src, dest))

        if not dest.parent.exists():
            g_logger.debug("create dir: %s" % dest.parent)
            dest.parent.mkdir(parents=True)

        shutil.move(src, dest)

    @overrides
    def delete(self, source_dir: Path, dest: Path):
        g_logger.info("delete, move to safe zone: %s" % dest)

        self._move_to_safe_zone('deleted', source_dir, dest)
