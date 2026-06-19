from typing import List
from domain.entities import Flight
from services.strategies.base import BaseStrategy

class CheapestStrategy(BaseStrategy):
    def sort(self, flights: List[Flight]) -> List[Flight]:
        # Sort by base_price_brl ascending
        return sorted(flights, key=lambda f: f.base_price_brl)
