from fastapi import APIRouter
from app.api.routes import (
    projects,
    customers,
    transactions,
)

api_router = APIRouter()

api_router.include_router(projects.router)
api_router.include_router(customers.router)
api_router.include_router(transactions.router)