"""
AI Manga/Video Production Pipeline System
Backend Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, create_db_and_tables
from app.api import auth, users, projects, scripts, chapters, storyboards, assets, reviews, pipeline, models as model_config, websocket, storage, providers
from app.middleware.auth import AuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI Manga/Video Production Pipeline System",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Middleware
app.add_middleware(AuthMiddleware)

# API Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(scripts.router, prefix="/api/scripts", tags=["Scripts"])
app.include_router(chapters.router, prefix="/api/chapters", tags=["Chapters"])
app.include_router(storyboards.router, prefix="/api/storyboards", tags=["Storyboards"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])
app.include_router(model_config.router, prefix="/api/models", tags=["Model Configuration"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
app.include_router(storage.router, prefix="/api/storage", tags=["Storage"])
app.include_router(providers.router, prefix="/api/providers", tags=["AI Providers"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
