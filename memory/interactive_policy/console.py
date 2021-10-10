import abc
from pathlib import Path
from typing import List

from .base import InteractivePolicyBase


class ConsolePolicy(InteractivePolicyBase):
    @abc.abstractmethod
    def choose_to_keep(self, files: List[Path]) -> int:
        for i in range(len(files)):
            print(f'{i} - {files[i]}')

        index = int(input("Give me a index: "))
        return index
