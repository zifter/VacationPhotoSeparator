import abc
from pathlib import Path
from typing import List

from .base import InteractivePolicyBase


class SilentPolicy(InteractivePolicyBase):
    @abc.abstractmethod
    def choose_to_keep(self, files: List[Path]) -> int:
        return 0
