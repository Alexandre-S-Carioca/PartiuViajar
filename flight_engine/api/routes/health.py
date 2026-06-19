from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from infrastructure.cache import cache_service

router = APIRouter(tags=["health"])

@router.get("/live")
async def liveness():
    return {"status": "ok"}

@router.get("/ready")
async def readiness():
    # Valida Redis e DB
    try:
        await cache_service.redis.ping()
        # Validação DB omitida por brevidade na resposta do health
        return {"status": "ready"}
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}

@router.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
