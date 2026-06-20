from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, health, patients
from app.core.config import get_settings
from app.core.database import engine
from app.core.quiver_client import ensure_collections
from app.models import *  # noqa: F401, F403 — ensure all models are registered

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.check_production_secrets()
    await ensure_collections()
    yield
    await engine.dispose()


app = FastAPI(
    title="Pulse API",
    description="Aortic & endovascular surgery intelligence — from referral to recovery.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(patients.router)
