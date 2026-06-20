"""Tests for AI endpoints — Groq and Quiver are mocked throughout."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.quiver_client import get_quiver_client
from app.core.security import hash_password
from app.main import app
from app.models.user import User, UserRole

# ── Shared fixtures ────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def admin_user(db) -> User:
    user = User(
        email="admin-ai@test.pulse",
        hashed_password=hash_password("test-password"),
        full_name="AI Admin",
        role=UserRole.admin,
    )
    db.add(user)
    await db.flush()
    return user


@pytest_asyncio.fixture
async def ai_client(db, mock_quiver) -> AsyncClient:
    """HTTP client with DB + Quiver overridden."""
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_quiver_client] = lambda: mock_quiver

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def _token(ac: AsyncClient, user: User, password: str = "test-password") -> str:  # noqa: S107
    resp = await ac.post("/auth/login", json={"email": user.email, "password": password})
    return resp.json()["access_token"]


# ── /ai/knowledge ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_knowledge_lists_guidelines(ai_client, surgeon_user):
    token = await _token(ai_client, surgeon_user)
    resp = await ai_client.get("/ai/knowledge", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    types = {i["type"] for i in items}
    assert "guideline" in types
    assert "literature" in types


@pytest.mark.asyncio
async def test_knowledge_requires_auth(ai_client):
    resp = await ai_client.get("/ai/knowledge")
    assert resp.status_code == 403 or resp.status_code == 401


# ── /ai/chat (SSE) ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_chat_requires_groq_key(ai_client, surgeon_user):
    """Without a Groq key the endpoint returns 503."""
    token = await _token(ai_client, surgeon_user)
    with patch("app.api.routers.ai.get_settings") as mock_settings:
        s = MagicMock()
        s.groq_api_key = ""
        mock_settings.return_value = s
        resp = await ai_client.post(
            "/ai/chat",
            json={"message": "What is EVAR?"},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_chat_streams_sse(ai_client, surgeon_user):
    """With a mocked Groq key and retriever, the SSE stream yields tokens + done."""
    token = await _token(ai_client, surgeon_user)

    fake_chunk = MagicMock()
    fake_chunk.content = "EVAR is endovascular aneurysm repair."

    async def mock_astream(*_args, **_kwargs):
        yield fake_chunk

    with (
        patch("app.api.routers.ai.get_settings") as mock_settings,
        patch("app.ai.retriever.retrieve", new=AsyncMock(return_value=[])),
        patch("app.api.routers.ai.ChatGroq") as mock_groq,  # noqa: N806
    ):
        s = MagicMock()
        s.groq_api_key = "gsk_test"
        s.groq_model = "llama-3.3-70b-versatile"
        s.groq_temperature = 0.3
        mock_settings.return_value = s

        instance = MagicMock()
        instance.astream = mock_astream
        mock_groq.return_value = instance

        resp = await ai_client.post(
            "/ai/chat",
            json={"message": "What is EVAR?"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    body = resp.text
    assert "sources" in body
    assert "token" in body
    assert "done" in body


# ── /ai/patient-summary ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_patient_summary_requires_groq_key(ai_client, surgeon_user):
    token = await _token(ai_client, surgeon_user)
    with patch("app.api.routers.ai.get_settings") as mock_settings:
        s = MagicMock()
        s.groq_api_key = ""
        mock_settings.return_value = s
        resp = await ai_client.post(
            "/ai/patient-summary/PAT-NONEXISTENT",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_patient_summary_404_on_missing(ai_client, surgeon_user):
    token = await _token(ai_client, surgeon_user)
    with (
        patch("app.api.routers.ai.get_settings") as mock_settings,
        patch("app.ai.graph.run_summary", new=AsyncMock(return_value=("summary", []))),
    ):
        s = MagicMock()
        s.groq_api_key = "gsk_test"
        mock_settings.return_value = s
        resp = await ai_client.post(
            "/ai/patient-summary/DOES-NOT-EXIST",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 404


# ── retriever unit tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_retrieve_returns_empty_on_quiver_failure():
    """If Quiver is down, retrieve() degrades gracefully to []."""
    from app.ai.retriever import retrieve

    with (
        patch("app.ai.retriever.embed", new=AsyncMock(return_value=[0.0] * 384)),
        patch("app.ai.retriever.get_quiver_client") as mock_qv,
    ):
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mock_ctx.search = AsyncMock(side_effect=Exception("quiver down"))
        mock_qv.return_value = mock_ctx

        docs = await retrieve("test query")

    assert docs == []


@pytest.mark.asyncio
async def test_retrieve_resolves_guideline_body():
    """IDs like guideline-000 should map back to the full GUIDELINES_CORPUS text."""
    from unittest.mock import MagicMock

    from quiver import Match

    from app.ai.retriever import retrieve
    from app.seed.generators import GUIDELINES_CORPUS

    hit = Match(id="guideline-000", score=0.9, payload={"title": GUIDELINES_CORPUS[0]["title"]})

    with (
        patch("app.ai.retriever.embed", new=AsyncMock(return_value=[0.0] * 384)),
        patch("app.ai.retriever.get_settings") as mock_s,
        patch("app.ai.retriever.get_quiver_client") as mock_qv,
    ):
        s = MagicMock()
        s.rerank_enabled = False
        mock_s.return_value = s

        mock_ctx = AsyncMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_ctx)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mock_ctx.search = AsyncMock(side_effect=[[hit], []])
        mock_qv.return_value = mock_ctx

        docs = await retrieve("AAA surveillance")

    assert len(docs) == 1
    assert docs[0]["body"] == GUIDELINES_CORPUS[0]["body"]
    assert docs[0]["type"] == "guideline"


def test_all_knowledge_covers_both_types():
    from app.ai.retriever import all_knowledge
    from app.seed.generators import GUIDELINES_CORPUS, LITERATURE_CORPUS

    items = all_knowledge()
    assert len(items) == len(GUIDELINES_CORPUS) + len(LITERATURE_CORPUS)
    ids = {i["id"] for i in items}
    assert "guideline-000" in ids
    assert "literature-000" in ids
