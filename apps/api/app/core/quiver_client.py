from quiver import AsyncClient, Client

from app.core.config import get_settings

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


def get_sync_quiver_client() -> Client:
    return Client(settings.quiver_url, api_key=settings.quiver_api_key)


def get_quiver_client() -> AsyncClient:
    return AsyncClient(settings.quiver_url, api_key=settings.quiver_api_key)


async def ensure_collections() -> None:
    """Create all knowledge-base collections if they don't already exist."""
    async with get_quiver_client() as q:
        existing = {c.name for c in await q.list_collections()}
        for name in ALL_COLLECTIONS:
            if name not in existing:
                await q.create_collection(name, dim=EMBEDDING_DIM, metric="cosine")
