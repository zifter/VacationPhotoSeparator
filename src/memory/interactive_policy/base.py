import abc
from typing import List


class InteractivePolicyBase:
    def __init__(self):
        pass

    @abc.abstractmethod
    def select_choice(self, header: str, choices: List[str], by_default=0) -> int:
        raise NotImplementedError()
