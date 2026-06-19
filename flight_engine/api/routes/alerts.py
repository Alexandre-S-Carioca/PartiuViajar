from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from decimal import Decimal
from infrastructure.db import get_db_session
from infrastructure.models import PriceAlertModel

router = APIRouter(prefix="/api/v1/flights/alerts", tags=["alerts"])

class CreatePriceAlertRequest(BaseModel):
    email: str
    telegram_chat_id: str = None
    origin: str
    destination: str
    departure_date: str
    target_price: float

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_price_alert(
    req: CreatePriceAlertRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Create a new price alert subscription.
    """
    try:
        # Strip timestamp details if they were passed, just match date
        date_str = req.departure_date.split("T")[0]
        dep_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD")

    alert = PriceAlertModel(
        email=req.email,
        telegram_chat_id=req.telegram_chat_id,
        origin=req.origin.strip().upper(),
        destination=req.destination.strip().upper(),
        departure_date=dep_date,
        target_price=Decimal(str(req.target_price))
    )

    db.add(alert)
    await db.commit()
    return {"status": "success", "message": "Alerta de preço cadastrado com sucesso!"}
