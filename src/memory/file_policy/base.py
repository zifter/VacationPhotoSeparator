import abc
from pathlib import Path


class FilePolicyBase:
    @abc.abstractmethod
    def failed_to_detected_original_date(self,  source_dir: Path, src: Path):
        raise NotImplementedError()

    @abc.abstractmethod
    def blacklist_file(self, source_dir: Path, src: Path):
        raise NotImplementedError()

    @abc.abstractmethod
    def move(self, src: Path, dest: Path):
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, source_dir: Path, dest: Path):
        raise NotImplementedError()

