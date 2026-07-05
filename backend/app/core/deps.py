from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import verify_supabase_jwt
from app.db import SessionLocal
from app.models import Profile

_bearer = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[Session, Depends(get_db)],
) -> Profile:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    payload = verify_supabase_jwt(creds.credentials)
    profile = db.get(Profile, UUID(payload["sub"]))
    if profile is None:
        # Signed-up user whose profiles row is missing means the signup trigger
        # is broken — surface it loudly rather than auto-creating a row here.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Profile not found")
    return profile


def require_admin(
    user: Annotated[Profile, Depends(get_current_user)],
) -> Profile:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return user
