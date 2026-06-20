from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import AsyncSessionLocal
from app.core.quiver_client import get_quiver_client
from app.core.redis_client import get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    checks: dict[str, str] = {"status": "ok"}

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception as e:
        checks["db"] = f"error: {e}"
        checks["status"] = "degraded"

    try:
        redis = get_redis()
        await redis.ping()
        await redis.aclose()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"
        checks["status"] = "degraded"

    try:
        async with get_quiver_client() as q:
            await q.list_collections()
        checks["quiver"] = "ok"
    except Exception as e:
        checks["quiver"] = f"error: {e}"
        checks["status"] = "degraded"

    return checks
