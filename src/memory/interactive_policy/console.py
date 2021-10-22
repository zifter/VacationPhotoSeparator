import abc
from pathlib import Path
from typing import List

from .base import InteractivePolicyBase


class ConsolePolicy(InteractivePolicyBase):
    @abc.abstractmethod
    def choose_to_keep(self, files: List[Path]) -> int:
        while True:
            try:
                print(f'>')
                for i, value in enumerate(files):
                    print(f'{i} - {value}')

                print(f'{-1} - keep all')

                index = int(input("Give me a index to keep: "))
                if index < -1 or index > len(files):
                    raise ValueError('')

                return index
            except ValueError:
                pass
            except KeyboardInterrupt:
                raise
