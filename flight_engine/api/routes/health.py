from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from infrastructure.cache import cache_service
from infrastructure.db import AsyncSessionLocal
from sqlalchemy import text

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    # Check Redis
    redis_ok = False
    try:
        await cache_service.redis.ping()
        redis_ok = True
    except Exception:
        pass

    # Check DB
    db_ok = False
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass

    status = "healthy" if (redis_ok and db_ok) else "unhealthy"
    content = {
        "status": status,
        "redis": "connected" if redis_ok else "disconnected",
        "database": "connected" if db_ok else "disconnected"
    }
    
    status_code = 200 if status == "healthy" else 500
    return JSONResponse(status_code=status_code, content=content)

@router.get("/live")
async def liveness():
    return {"status": "ok"}

@router.get("/ready")
async def readiness():
    try:
        await cache_service.redis.ping()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}

@router.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

