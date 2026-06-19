from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from infrastructure.db import get_db_session
from infrastructure.models import FlightPriceHistoryModel, FlightModel
from typing import List, Dict

router = APIRouter(prefix="/api/v1/flights", tags=["flights"])

@router.get("/price-history", response_model=List[Dict])
async def get_price_history(
    flight_id: str = Query(..., description="ID of the flight to fetch history for"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get the price history of a specific flight.
    If no history or only one point exists in the DB, mock fallback historical points are generated
    for a richer visual experience on the frontend graph.
    """
    stmt = (
        select(FlightPriceHistoryModel)
        .where(FlightPriceHistoryModel.flight_id == flight_id)
        .order_by(FlightPriceHistoryModel.recorded_at.asc())
    )
    result = await db.execute(stmt)
    history = result.scalars().all()

    # Get flight base price to use as reference if needed
    flight_stmt = select(FlightModel).where(FlightModel.id == flight_id)
    flight_res = await db.execute(flight_stmt)
    flight_obj = flight_res.scalar_one_or_none()
    
    base_price = float(flight_obj.price) if flight_obj else (float(history[0].price) if history else 1200.0)

    if len(history) <= 1:
        # Generate some mock past points for a beautiful chart experience
        import random
        from datetime import datetime, timedelta
        
        mock_points = []
        now = datetime.now()
        
        # Base prices on last 5 days
        for i in range(5, 0, -1):
            date_point = now - timedelta(days=i)
            # Vary price slightly (between -12% and +8%)
            variation = random.uniform(-0.12, 0.08)
            mock_price = round(base_price * (1 + variation), 2)
            mock_points.append({
                "price": mock_price,
                "date": date_point.strftime("%d/%m")
            })
            
        # Add the current price
        mock_points.append({
            "price": base_price,
            "date": now.strftime("%d/%m")
        })
        return mock_points

    return [
        {
            "price": float(h.price),
            "date": h.recorded_at.strftime("%d/%m %H:%M")
        } for h in history
    ]
