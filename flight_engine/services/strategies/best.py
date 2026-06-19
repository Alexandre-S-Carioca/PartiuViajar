from typing import List
from domain.entities import Flight
from services.strategies.base import BaseStrategy

class BestStrategy(BaseStrategy):
    def sort(self, flights: List[Flight]) -> List[Flight]:
        # Sort by: 1. Base Price (BRL), 2. Duration, 3. Stops
        return sorted(flights, key=lambda f: (f.base_price_brl, f.duration, f.stops))
