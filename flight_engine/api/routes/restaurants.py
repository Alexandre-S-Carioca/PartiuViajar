from fastapi import APIRouter, Query
from typing import List, Optional
from infrastructure.clients.tripadvisor_client import tripadvisor_client

router = APIRouter(prefix="/api/v1/restaurants", tags=["restaurants"])


@router.get("")
async def get_restaurants_by_location(
    location_id: Optional[int] = Query(None, description="TripAdvisor locationId"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    limit: int = Query(20, le=30),
):
    """
    Retorna restaurantes por locationId do TripAdvisor ou por coordenadas geográficas.
    Exemplos:
      - /api/v1/restaurants?location_id=304554        (Fortaleza)
      - /api/v1/restaurants?lat=-3.71&lon=-38.54
    """
    if location_id:
        return await tripadvisor_client.search_by_location_id(location_id, limit)
    elif lat is not None and lon is not None:
        return await tripadvisor_client.search_by_geo(lat, lon, limit)
    else:
        return {"error": "Informe location_id ou lat+lon"}
