"""
Transaction CRUD endpoints, scoped under a customer:
GET/POST /customers/{id}/transactions, PUT/DELETE /transactions/{id}.
See docs/api/API-Design.md. To be implemented in Module 2.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# Endpoints go here. Once implemented, wire this into routes/__init__.py.
