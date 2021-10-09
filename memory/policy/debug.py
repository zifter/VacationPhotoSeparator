from pathlib import Path

from overrides import overrides

from logger import g_logger
from policy.base import FilePolicyBase


class DebugFilePolicy(FilePolicyBase):
    @overrides
    def move(self, src: Path, dest: Path):
        g_logger.debug("move called: %s -> %s" % (src, dest))

    @overrides
    def delete(self, source_dir: Path, dest: Path):
        g_logger.debug("delete called: %s" % dest)
