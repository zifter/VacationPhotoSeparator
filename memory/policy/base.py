import abc
from pathlib import Path


class FilePolicyBase(object):
    def __init__(self):
        pass

    @abc.abstractmethod
    def move(self, src: Path, dest: Path):
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, source_dir: Path, dest: Path):
        raise NotImplementedError()

