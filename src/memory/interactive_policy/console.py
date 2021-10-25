import abc
from typing import List

from .base import InteractivePolicyBase


class ConsolePolicy(InteractivePolicyBase):
    @abc.abstractmethod
    def select_choice(self, header: str, choices: List[str], by_default=0) -> int:
        while True:
            try:
                print(header)
                for i, value in enumerate(choices):
                    print(f'{i} - {value}')

                print(f'{-1} - skip')

                index = int(input("Give me a choice index: "))
                if index < -1 or index > len(choices):
                    raise ValueError('')

                return index
            except ValueError:
                pass
            except KeyboardInterrupt:
                raise
