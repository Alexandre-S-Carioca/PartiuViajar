from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from infrastructure.db import AsyncSessionLocal
from infrastructure.models import SearchHistoryModel

router = APIRouter(prefix="/api/search-history", tags=["history"])


@router.get("")
async def get_search_history():
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(SearchHistoryModel).order_by(SearchHistoryModel.searched_at.desc()).limit(20)
            res = await session.execute(stmt)
            records = res.scalars().all()

            return [
                {
                    "id": r.id,
                    "origin": r.origin,
                    "destination": r.destination,
                    "departure_date": r.departure_date.strftime("%Y-%m-%d"),
                    "return_date": r.return_date.strftime("%Y-%m-%d") if r.return_date else None,
                    "adults": r.adults,
                    "searched_at": r.searched_at.isoformat(),
                }
                for r in records
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
