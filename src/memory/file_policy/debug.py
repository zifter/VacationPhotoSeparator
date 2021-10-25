from pathlib import Path

from overrides import overrides

from ..logger import g_logger
from .base import FilePolicyBase


class DebugFilePolicy(FilePolicyBase):
    @overrides
    def failed_to_detected_original_date(self,  source_dir: Path, src: Path):
        g_logger.debug("failed to detect original date: %s" % src)

    @overrides
    def blacklist_file(self, source_dir: Path, src: Path):
        g_logger.debug("ignore file: %s", src)

    @overrides
    def move(self, src: Path, dest: Path):
        g_logger.debug("move: %s -> %s", src, dest)

    @overrides
    def delete(self, source_dir: Path, dest: Path):
        g_logger.debug("delete: %s", dest)
