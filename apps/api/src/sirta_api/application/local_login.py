"""Operator login. The public bootstrap session stays unable to change users."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import AccessPurpose, User
from sirta_api.adapters.db.synthetic_ids import AUDIENCE, ISSUER
from sirta_api.application.audit import record_audit
from sirta_api.config import Settings
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ForbiddenError, UnauthorizedError
from sirta_api.domain.identities import Role
from sirta_api.domain.local_login import SESSION_MODE, confirm_login


def login_operator(session: Session, *, settings: Settings, payload: dict) -> dict:
    username = str(payload.get("username") or "").strip()
    password = str(payload.get("password") or "")
    user = session.scalar(select(User).where(User.username == username))
    confirm_login(
        active=bool(user and user.active),
        password_hash=user.password_hash if user else None,
        password=password,
    )
    if user is None:
        raise UnauthorizedError("Acesso não conferiu.")
    territory = sorted(user.territories, key=lambda item: item.name)
    if not territory:
        raise UnauthorizedError("Acesso não conferiu.")
    now = datetime.now(UTC)
    purposes = session.scalars(
        select(AccessPurpose).where(AccessPurpose.tenant_id == user.tenant_id)
    ).all()
    purpose = next(
        (row for row in purposes if row.expires_at is None or row.expires_at > now),
        None,
    )
    if purpose is None:
        raise UnauthorizedError("Acesso não conferiu.")
    expires = now + timedelta(hours=8)
    token = _token(user, settings, now, expires)
    context = AccessContext(
        user_id=user.id,
        tenant_id=user.tenant_id,
        territory_id=territory[0].id,
        purpose_id=purpose.id,
        role=Role(user.role),
        purpose_expires_at=purpose.expires_at,
        username=user.username,
        session_mode=SESSION_MODE,
    )
    record_audit(
        session,
        context=context,
        action="auth.operator_login",
        route="/v1/auth/login",
        outcome="ALLOWED",
        resource_type="session",
        resource_id=user.id,
    )
    session.commit()
    return {
        "accessToken": token,
        "tokenType": "Bearer",
        "expiresAt": expires.isoformat(),
        "territoryId": str(territory[0].id),
        "purposeId": str(purpose.id),
        "tenantId": str(user.tenant_id),
        "username": user.username,
        "role": user.role,
        "mode": SESSION_MODE,
        "createsTaxCredit": False,
    }


def _token(user: User, settings: Settings, now: datetime, expires: datetime) -> str:
    key_path = settings.oidc_signing_key_path
    if not key_path:
        raise ForbiddenError("OIDC signing key is not configured")
    private_key = Path(key_path).read_bytes()
    return jwt.encode(
        {
            "sub": user.subject,
            "iss": settings.oidc_issuer or ISSUER,
            "aud": settings.oidc_audience or AUDIENCE,
            "iat": now,
            "exp": expires,
            "tenant_id": str(user.tenant_id),
            "amr": ["pwd", "mfa"],
            "sirta_session": SESSION_MODE,
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "sirta-test"},
    )
