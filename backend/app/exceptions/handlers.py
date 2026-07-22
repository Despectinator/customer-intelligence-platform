"""
FastAPI exception handlers: registers the custom exceptions from
custom_exceptions.py and maps them to consistent HTTP error responses,
matching the {"success": false, "message": "..."} format documented in
docs/api/API-Design.md.

To be wired into app/main.py once custom_exceptions.py has real exceptions
to handle.
"""
