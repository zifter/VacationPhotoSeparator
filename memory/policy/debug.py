from pathlib import Path

from overrides import overrides

from ..logger import g_logger
from .base import FilePolicyBase


class DebugFilePolicy(FilePolicyBase):
    @overrides
    def move(self, src: Path, dest: Path):
        g_logger.debug("move: %s -> %s" % (src, dest))

    @overrides
    def delete(self, source_dir: Path, dest: Path):
        g_logger.debug("delete: %s" % dest)
