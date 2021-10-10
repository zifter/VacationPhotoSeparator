import abc
from pathlib import Path
from typing import List


class InteractivePolicyBase:
    def __init__(self):
        pass

    @abc.abstractmethod
    def choose_to_keep(self, files: List[Path]) -> Path:
        raise NotImplementedError()
