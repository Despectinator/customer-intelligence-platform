from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.core.security import verify_token, CurrentUser

security = HTTPBearer()


def get_db():
    """Yields a DB session for the duration of one request, then closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    """
    Verifies the Supabase JWT sent by the frontend and returns the
    authenticated user. Raises 401 if the token is missing/invalid/expired.
    """
    user = verify_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return user
