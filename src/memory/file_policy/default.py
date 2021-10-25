import os
import shutil
from pathlib import Path

from overrides import overrides

from ..logger import g_logger
from .base import FilePolicyBase


class DefaultFilePolicy(FilePolicyBase):
    @overrides
    def failed_to_detected_original_date(self,  source_dir: Path, src: Path):
        g_logger.info("skip: %s", src)

    @overrides
    def blacklist_file(self, source_dir: Path, src: Path):
        g_logger.info("ignore file: %s", src)

    @overrides
    def move(self, src: Path, dest: Path):
        g_logger.info("move: %s -> %s", src, dest)

        if not dest.parent.exists():
            g_logger.debug("create dir: %s", dest.parent)
            dest.parent.mkdir(parents=True)

        shutil.move(src, dest)

    @overrides
    def delete(self, source_dir: Path, dest: Path):
        g_logger.info("remove: %s", dest)
        os.remove(dest)
