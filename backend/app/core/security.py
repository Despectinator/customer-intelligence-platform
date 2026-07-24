import uuid

from pydantic import BaseModel
from supabase import Client, create_client

from app.core.config import settings


_supabase_client: Client | None = None


def _get_supabase_client() -> Client:
    """
    Lazily create and cache the Supabase client.
    """
    global _supabase_client

    if _supabase_client is None:
        settings.validate()
        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
        )

    return _supabase_client


class CurrentUser(BaseModel):
    """
    Minimal representation of the authenticated user.
    """

    id: uuid.UUID
    email: str | None = None


def verify_token(token: str) -> CurrentUser | None:
    """
    Verify a Supabase JWT and return the authenticated user.
    """

    supabase = _get_supabase_client()

    try:
        response = supabase.auth.get_user(token)
        user = response.user

        if user is None:
            return None

        return CurrentUser(
            id=user.id,
            email=user.email,
        )

    except Exception as e:
        print("=" * 60)
        print("SUPABASE AUTH ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 60)
        return None