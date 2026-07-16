import asyncio

import structlog
from quiver import AsyncClient, Client, QuiverError

from app.core.config import get_settings

log = structlog.get_logger()
settings = get_settings()

COLLECTION_PATIENTS = "patients"
COLLECTION_DEVICES = "devices"
COLLECTION_GUIDELINES = "guidelines"
COLLECTION_LITERATURE = "literature"
COLLECTION_NOTES = "notes"

ALL_COLLECTIONS = [
    COLLECTION_PATIENTS,
    COLLECTION_DEVICES,
    COLLECTION_GUIDELINES,
    COLLECTION_LITERATURE,
    COLLECTION_NOTES,
]

EMBEDDING_DIM = 384  # BAAI/bge-small-en-v1.5
METRIC = "cosine"


def get_sync_quiver_client() -> Client:
    return Client(settings.quiver_url, api_key=settings.quiver_api_key)


def get_quiver_client() -> AsyncClient:
    return AsyncClient(settings.quiver_url, api_key=settings.quiver_api_key)


async def ensure_collections(retries: int = 10, delay: float = 3.0) -> None:
    """Create the knowledge-base collections if they don't already exist.

    Retries while Quiver is still starting up (it comes up alongside the API in
    Compose) and degrades gracefully if it never becomes reachable — the vector
    store is optional and retrieval already falls back to an empty result set.
    """
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            async with get_quiver_client() as q:
                existing = {c.name for c in await q.list_collections()}
                for name in ALL_COLLECTIONS:
                    if name in existing:
                        continue
                    try:
                        await q.create_collection(name, dim=EMBEDDING_DIM, metric=METRIC)
                    except QuiverError as exc:
                        # 409 = created concurrently; anything else is a real error.
                        if getattr(exc, "status", None) != 409:
                            raise
            return
        except Exception as exc:  # startup resilience — Quiver may not be ready yet
            last_exc = exc
            if attempt < retries - 1:
                await asyncio.sleep(delay)
    log.warning(
        "quiver.ensure_collections unreachable after retries — AI retrieval degraded",
        error=str(last_exc),
    )
