"""
Customer CRUD endpoints, scoped under a project:
GET/POST /projects/{project_id}/customers, GET/PUT/DELETE /customers/{id}.
See docs/api/API-Design.md. To be implemented in Module 2.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/customers", tags=["Customers"])

# Endpoints go here. Once implemented, wire this into routes/__init__.py:
#   from app.api.routes import customers
#   api_router.include_router(customers.router)
