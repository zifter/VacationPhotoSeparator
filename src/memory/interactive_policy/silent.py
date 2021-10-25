import abc
from typing import List

from .base import InteractivePolicyBase


class SilentPolicy(InteractivePolicyBase):
    @abc.abstractmethod
    def select_choice(self, header: str, files: List[str], by_default=0) -> int:
        return by_default
