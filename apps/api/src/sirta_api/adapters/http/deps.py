from datetime import UTC, datetime
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import AccessPurpose, User
from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.oidc.jwt import decode_access_token
from sirta_api.config import get_settings
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ForbiddenError, UnauthorizedError
from sirta_api.domain.identities import Role


def get_access_context(
    request: Request,
    session: Session = Depends(get_session),
) -> AccessContext:
    authorization = request.headers.get("authorization", "")
    if not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Bearer token is required")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise UnauthorizedError("Bearer token is required")

    claims = decode_access_token(token, get_settings())
    subject = claims.get("sub")
    tenant_claim = claims.get("tenant_id")
    if not subject or not tenant_claim:
        raise ForbiddenError("Token is missing tenant or subject claims")

    user = session.scalar(select(User).where(User.subject == subject))
    if user is None:
        raise ForbiddenError("User is not provisioned")
    try:
        token_tenant = UUID(str(tenant_claim))
    except ValueError as exc:
        raise ForbiddenError("Token tenant is invalid") from exc
    if user.tenant_id != token_tenant:
        raise ForbiddenError("Token tenant does not match the provisioned user")

    territory_header = request.headers.get("x-territory-id")
    purpose_header = request.headers.get("x-purpose-id")
    if not territory_header or not purpose_header:
        raise ForbiddenError("Territory and access purpose are required")
    try:
        territory_id = UUID(territory_header)
        purpose_id = UUID(purpose_header)
    except ValueError as exc:
        raise ForbiddenError("Territory or access purpose is invalid") from exc

    allowed = {item.id for item in user.territories}
    context = AccessContext(
        user_id=user.id,
        tenant_id=user.tenant_id,
        territory_id=territory_id,
        purpose_id=purpose_id,
        role=Role(user.role),
        purpose_expires_at=None,
        username=user.username,
    )
    context.ensure_territory_allowed(allowed)

    purpose = session.get(AccessPurpose, purpose_id)
    if purpose is None or purpose.tenant_id != user.tenant_id:
        raise ForbiddenError("Access purpose is not valid for this tenant")
    context = AccessContext(
        user_id=user.id,
        tenant_id=user.tenant_id,
        territory_id=territory_id,
        purpose_id=purpose_id,
        role=Role(user.role),
        purpose_expires_at=purpose.expires_at,
        username=user.username,
    )
    context.ensure_purpose_active(datetime.now(UTC))
    request.state.access_context = context
    return context
