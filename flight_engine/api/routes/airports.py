from fastapi import APIRouter, Query
from typing import List, Dict
from services.airport_service import airport_service

router = APIRouter(prefix="/api/v1/flights/airports", tags=["airports"])

@router.get("/search", response_model=List[Dict[str, str]])
async def search_airports(q: str = Query("", description="Query text to search airports (city, code, name, country)")):
    """
    Search for airports matching a given query.
    Returns a list of matching airports (maximum 8 results).
    """
    return airport_service.search(q)

@router.get("/cities/search", response_model=List[Dict[str, str]])
async def search_cities(q: str = Query("", description="Query text to search cities")):
    """
    Search for unique cities worldwide matching a given query.
    """
    return await airport_service.search_cities(q)

@router.get("/geo_cities/search", response_model=List[Dict[str, str]])
async def search_geo_cities(q: str = Query("", description="Query text to search cities (Geo API)")):
    """
    Search for pure cities using Geo API without airport matching.
    Returns: [{"display": "City, Country", "city": "City", "country": "Country"}]
    """
    from infrastructure.clients.geo_client import geo_api_client
    if not q: return []
    
    cities = await geo_api_client.search_cities(q)
    results = []
    seen = set()
    for c in cities:
        city_name = c.get("name")
        country_name = c.get("country", {}).get("name") if isinstance(c.get("country"), dict) else "Unknown"
        
        # O Geo API pode retornar strings no dict country se der erro, tratamos por precaução
        if not city_name: continue
            
        key = f"{city_name}-{country_name}"
        if key not in seen:
            seen.add(key)
            results.append({
                "display": f"{city_name}, {country_name}",
                "city": city_name,
                "country": country_name,
                "name": "City"
            })
            if len(results) >= 8: break
            
    return results
