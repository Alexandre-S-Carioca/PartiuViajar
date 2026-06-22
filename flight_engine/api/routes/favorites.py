from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from infrastructure.db import AsyncSessionLocal
from infrastructure.models import FavoriteModel

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


class FavoriteRequest(BaseModel):
    item_type: str  # 'flight' or 'accommodation'
    item_id: str
    details: dict


@router.get("")
async def get_favorites():
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(FavoriteModel).order_by(FavoriteModel.created_at.desc())
            res = await session.execute(stmt)
            records = res.scalars().all()

            return [
                {
                    "id": r.id,
                    "item_type": r.item_type,
                    "item_id": r.item_id,
                    "details": r.details,
                    "created_at": r.created_at.isoformat(),
                }
                for r in records
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def toggle_favorite(req: FavoriteRequest):
    if req.item_type not in ["flight", "accommodation"]:
        raise HTTPException(status_code=400, detail="Invalid item_type. Must be 'flight' or 'accommodation'.")

    try:
        async with AsyncSessionLocal() as session:
            # Check if already exists
            stmt = select(FavoriteModel).where(
                (FavoriteModel.item_type == req.item_type) & (FavoriteModel.item_id == req.item_id)
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if existing:
                # Remove from favorites
                await session.delete(existing)
                await session.commit()
                return {"status": "removed", "message": "Item removed from favorites."}
            else:
                # Add to favorites
                fav = FavoriteModel(item_type=req.item_type, item_id=req.item_id, details=req.details)
                session.add(fav)
                await session.commit()
                return {"status": "added", "message": "Item added to favorites."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
