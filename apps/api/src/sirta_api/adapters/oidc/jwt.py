from __future__ import annotations

import json
from pathlib import Path

import httpx
import jwt
from jwt import PyJWK

from sirta_api.config import Settings
from sirta_api.domain.errors import UnauthorizedError


def decode_access_token(token: str, settings: Settings) -> dict:
    try:
        header = jwt.get_unverified_header(token)
        key = _key_for_kid(header.get("kid"), settings)
        return jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
        )
    except UnauthorizedError:
        raise
    except Exception as exc:
        raise UnauthorizedError("Invalid access token") from exc


def _key_for_kid(kid: str | None, settings: Settings):
    jwks = _load_jwks(settings)
    for item in jwks.get("keys", []):
        if kid is None or item.get("kid") == kid:
            return PyJWK.from_dict(item).key
    raise UnauthorizedError("Token signing key was not found")


def _load_jwks(settings: Settings) -> dict:
    if settings.oidc_jwks_path:
        return json.loads(Path(settings.oidc_jwks_path).read_text(encoding="utf-8"))
    if not settings.oidc_jwks_url:
        raise UnauthorizedError("OIDC JWKS is not configured")
    response = httpx.get(settings.oidc_jwks_url, timeout=2.0)
    response.raise_for_status()
    return response.json()
