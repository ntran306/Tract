import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

from app.core.config import get_settings

_jwk_client: PyJWKClient | None = None


def _get_jwk_client() -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        _jwk_client = PyJWKClient(get_settings().jwks_url, cache_keys=True)
    return _jwk_client


def verify_supabase_jwt(token: str) -> dict:
    """Verify a Supabase access token and return its claims.

    New Supabase projects sign with asymmetric keys (JWKS/ES256); legacy projects
    use an HS256 shared secret. SUPABASE_JWT_SECRET being set selects legacy mode.
    """
    settings = get_settings()
    try:
        if settings.supabase_jwt_secret:
            return jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
        signing_key = _get_jwk_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid or expired token"
        ) from exc
