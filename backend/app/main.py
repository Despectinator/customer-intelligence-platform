import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import api_router
from app.core.config import settings
from app.database.database import get_db
from app.exceptions.handlers import register_exception_handlers

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger("app")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CustomerLens - Customer Intelligence Platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# Register all API routes
app.include_router(api_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health/database")
def database_health(db: Session = Depends(get_db)):
    """
    Check database connectivity. This endpoint is intentionally
    unauthenticated (health checks/load balancers usually can't
    authenticate), which is exactly why it must never leak raw exception
    details — the real error is logged server-side only; the response
    only ever says "connected" or "disconnected."
    """
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception:
        logger.exception("Database health check failed")
        return {
            "status": "unhealthy",
            "database": "disconnected",
        }