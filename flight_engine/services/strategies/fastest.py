from typing import List
from domain.entities import Flight
from services.strategies.base import BaseStrategy

class FastestStrategy(BaseStrategy):
    def sort(self, flights: List[Flight]) -> List[Flight]:
        # Sort by duration ascending
        return sorted(flights, key=lambda f: f.duration)
