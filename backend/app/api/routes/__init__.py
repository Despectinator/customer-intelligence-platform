from fastapi import APIRouter

from app.api.routes import projects, customers

api_router = APIRouter()

api_router.include_router(projects.router)
api_router.include_router(customers.router)