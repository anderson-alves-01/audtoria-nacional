"""Mint short-lived PUBLIC_OPEN UI sessions for validation stacks without IdP."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
from sqlalchemy.orm import Session

from sirta_api.adapters.db.synthetic_ids import (
    AUDIENCE,
    ISSUER,
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ANALYST_ALPHA,
)
from sirta_api.application.audit import record_audit
from sirta_api.config import Settings
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ForbiddenError
from sirta_api.domain.identities import Role


def mint_public_open_session(session: Session, *, settings: Settings) -> dict:
    if not settings.public_open_ui_bootstrap:
        raise ForbiddenError("PUBLIC_OPEN UI bootstrap is disabled")
    key_path = settings.oidc_signing_key_path
    if not key_path:
        raise ForbiddenError("OIDC signing key is not configured")
    private_key = Path(key_path).read_bytes()
    now = datetime.now(UTC)
    expires = now + timedelta(hours=8)
    token = jwt.encode(
        {
            "sub": str(USER_ANALYST_ALPHA),
            "iss": settings.oidc_issuer or ISSUER,
            "aud": settings.oidc_audience or AUDIENCE,
            "iat": now,
            "exp": expires,
            "tenant_id": str(TENANT_ALPHA),
            "amr": ["pwd", "mfa"],
            "sirta_session": "PUBLIC_OPEN_UI_BOOTSTRAP",
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "sirta-test"},
    )
    context = AccessContext(
        user_id=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
        role=Role.ANALYST,
        purpose_expires_at=expires,
        username="analyst.alpha",
    )
    record_audit(
        session,
        context=context,
        action="auth.public_open_session.mint",
        route="/v1/auth/public-open-session",
        outcome="ALLOWED",
        resource_type="session",
        resource_id=USER_ANALYST_ALPHA,
    )
    session.commit()
    return {
        "accessToken": token,
        "tokenType": "Bearer",
        "expiresAt": expires.isoformat(),
        "territoryId": str(TERRITORY_ALPHA_CENTRO),
        "purposeId": str(PURPOSE_ALPHA_ACTIVE),
        "tenantId": str(TENANT_ALPHA),
        "subject": str(USER_ANALYST_ALPHA),
        "mode": "PUBLIC_OPEN_UI_BOOTSTRAP",
        "createsTaxCredit": False,
        "note": (
            "Sessão de validação PUBLIC_OPEN. Não é IdP institucional. "
            "Comandos de crédito permanecem desativados."
        ),
    }
