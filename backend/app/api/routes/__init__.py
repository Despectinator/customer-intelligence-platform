from fastapi import APIRouter
from app.api.routes import (
    projects,
    customers,
    transactions,
    analytics,
    upload,
)

api_router = APIRouter()

api_router.include_router(projects.router)
api_router.include_router(customers.router)
api_router.include_router(transactions.router)
api_router.include_router(analytics.router)
api_router.include_router(upload.router)
