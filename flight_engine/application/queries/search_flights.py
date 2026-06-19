from typing import List
from application.dto.flight_dto import SearchFlightRequest, FlightDTO
from services.search_service import search_service

class SearchFlightsQueryHandler:
    async def handle(self, request: SearchFlightRequest) -> List[FlightDTO]:
        # This acts as the Query portion of CQRS
        # It takes a simple DTO, calls the domain service, and returns simple DTOs.
        domain_flights = await search_service.search_v2(request)
        
        # Convert domain entities to Pydantic DTOs for the API layer
        return [
            FlightDTO(
                id=f.id,
                airline=f.airline,
                origin=f.origin,
                destination=f.destination,
                departure_date=f.departure_date,
                arrival_date=f.arrival_date,
                price=f.price,
                currency=f.currency,
                base_price_brl=f.base_price_brl,
                duration=f.duration,
                stops=f.stops,
                cabin_class=f.cabin_class,
                booking_url=f.booking_url,
                collected_at=f.collected_at
            ) for f in domain_flights
        ]

search_flights_query_handler = SearchFlightsQueryHandler()
