import shutil
from pathlib import Path

from overrides import overrides

from logger import g_logger
from policy.base import FilePolicyBase


class SafeFilePolicy(FilePolicyBase):
    def __init__(self, safe_dir: Path):
        super().__init__()

        self.safe_dir = safe_dir

    @overrides
    def move(self, src: Path, dest: Path):
        g_logger.info("copy: %s -> %s" % (src, dest))

        if not dest.parent.exists():
            g_logger.debug("create dir: %s" % dest.parent)
            dest.parent.mkdir()

        shutil.copy(src, dest)

    @overrides
    def delete(self, source_dir: Path, dest: Path):
        relative = dest.relative_to(source_dir)

        move_to = self.safe_dir.joinpath(relative)

        if not move_to.parent.exists():
            move_to.parent.mkdir()

        i = 0
        while move_to.exists():
            move_to = move_to.rename(move_to.name + f'_duplicated_{i}')
            i += 1

        shutil.copy(dest, move_to)
