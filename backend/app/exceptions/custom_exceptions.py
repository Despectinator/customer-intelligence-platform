"""
Application-specific exception base class.

Note on this codebase's actual pattern: services throughout this app
(project_service, customer_service, transaction_service, etc.) raise
FastAPI's HTTPException directly rather than custom exception classes —
that's an established, tested, working pattern, and this file doesn't
replace it. AppException exists for a narrower purpose: signaling
internal/business-logic errors that aren't naturally an HTTP concern at
the point they're raised (e.g. deep inside app/ml/ or app/analytics/,
which know nothing about HTTP status codes). handlers.py catches these
and translates them to a clean response.
"""


class AppException(Exception):
    """Base class for application-specific errors that aren't naturally HTTP-shaped."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
