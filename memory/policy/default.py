import os
import shutil
from pathlib import Path

from overrides import overrides

from logger import g_logger
from policy.base import FilePolicyBase


class DefaultFilePolicy(FilePolicyBase):
    @overrides
    def move(self, src: Path, dest: Path):
        g_logger.info("move: %s -> %s" % (src, dest))

        if not dest.parent.exists():
            g_logger.debug("create dir: %s" % dest.parent)
            dest.parent.mkdir()

        shutil.move(src, dest)

    @overrides
    def delete(self, source_dir: Path, dest: Path):
        g_logger.info("remove: %s" % dest)
        os.remove(dest)
