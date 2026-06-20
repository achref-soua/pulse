from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.quiver_client import get_quiver_client
from app.main import app
from app.models.user import User, UserRole
from app.core.security import hash_password

TEST_DB_URL = "postgresql+asyncpg://pulse:pulse_test@localhost:5432/pulse_test"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    _engine = create_async_engine(TEST_DB_URL, echo=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_quiver():
    mock = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    mock.list_collections = AsyncMock(return_value=[])
    mock.create_collection = AsyncMock()
    mock.upsert = AsyncMock()
    mock.search = AsyncMock(return_value=[])
    return mock


@pytest.fixture
async def client(db, mock_quiver) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_quiver_client] = lambda: mock_quiver

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def surgeon_user(db) -> User:
    user = User(
        email="surgeon@test.pulse",
        hashed_password=hash_password("test-password"),
        full_name="Test Surgeon",
        role=UserRole.surgeon,
    )
    db.add(user)
    await db.flush()
    return user
