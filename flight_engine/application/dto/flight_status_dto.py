from pydantic import BaseModel
from typing import Optional, Dict, Any

class FlightStatusDTO(BaseModel):
    flight_date: Optional[str]
    flight_status: Optional[str]
    
    departure_airport: Optional[str]
    departure_timezone: Optional[str]
    departure_iata: Optional[str]
    departure_scheduled: Optional[str]
    departure_actual: Optional[str]
    
    arrival_airport: Optional[str]
    arrival_timezone: Optional[str]
    arrival_iata: Optional[str]
    arrival_scheduled: Optional[str]
    arrival_delay: Optional[int]
    
    airline_name: Optional[str]
    airline_iata: Optional[str]
    
    flight_number: Optional[str]
    flight_iata: Optional[str]

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "FlightStatusDTO":
        dep = data.get("departure", {})
        arr = data.get("arrival", {})
        airline = data.get("airline", {})
        flight = data.get("flight", {})
        
        return cls(
            flight_date=data.get("flight_date"),
            flight_status=data.get("flight_status"),
            
            departure_airport=dep.get("airport"),
            departure_timezone=dep.get("timezone"),
            departure_iata=dep.get("iata"),
            departure_scheduled=dep.get("scheduled"),
            departure_actual=dep.get("actual"),
            
            arrival_airport=arr.get("airport"),
            arrival_timezone=arr.get("timezone"),
            arrival_iata=arr.get("iata"),
            arrival_scheduled=arr.get("scheduled"),
            arrival_delay=arr.get("delay"),
            
            airline_name=airline.get("name"),
            airline_iata=airline.get("iata"),
            
            flight_number=flight.get("number"),
            flight_iata=flight.get("iata")
        )
