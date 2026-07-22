import uuid
from supabase import create_client, Client

from app.core.config import settings

_supabase_client: Client | None = None


def _get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        settings.validate()
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client


class CurrentUser:
    """Minimal representation of the authenticated Supabase user."""

    def __init__(self, id: str, email: str | None):
        self.id = uuid.UUID(id)
        self.email = email


def verify_token(token: str) -> CurrentUser | None:
    """
    Verifies a Supabase-issued JWT by asking Supabase Auth to resolve it to a
    user. Returns None if the token is invalid/expired rather than raising —
    the caller (an API dependency) decides how to turn that into an HTTP error.
    """
    supabase = _get_supabase_client()
    try:
        response = supabase.auth.get_user(token)
        user = response.user
        if not user:
            return None
        return CurrentUser(id=user.id, email=user.email)
    except Exception:
        return None
