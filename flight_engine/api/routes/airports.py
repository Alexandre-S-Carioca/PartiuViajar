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
