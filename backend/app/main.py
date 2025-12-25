"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .core.database import create_tables
from .routers import participants, survey, dose_chatbot, results, satisfaction, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: create database tables
    await create_tables()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Psychological Assessment Chatbot API - Comparing traditional surveys with DOSE adaptive chatbot assessments",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(participants.router, prefix="/api/participants", tags=["Participants"])
app.include_router(survey.router, prefix="/api/survey", tags=["Survey (Traditional)"])
app.include_router(dose_chatbot.router, prefix="/api/dose", tags=["DOSE (Adaptive Chatbot)"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(satisfaction.router, prefix="/api/satisfaction", tags=["Satisfaction Survey"])
app.include_router(export.router, prefix="/api/export", tags=["Data Export"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
