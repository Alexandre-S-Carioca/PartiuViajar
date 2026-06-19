import abc
from typing import List
from domain.entities import Flight

class BaseStrategy(abc.ABC):
    @abc.abstractmethod
    def sort(self, flights: List[Flight]) -> List[Flight]:
        pass
