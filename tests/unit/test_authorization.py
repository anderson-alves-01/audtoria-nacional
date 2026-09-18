from datetime import UTC, datetime

from tests.fixtures.synthetic import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TENANT_BETA,
    TERRITORY_ALPHA_CENTRO,
    TERRITORY_ALPHA_NORTE,
    USER_ANALYST_ALPHA,
)

from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ForbiddenError, NotVisibleError
from sirta_api.domain.identities import Role


def _context(
    role: Role = Role.ANALYST, territory=TERRITORY_ALPHA_CENTRO, expires=None
) -> AccessContext:
    return AccessContext(
        user_id=USER_ANALYST_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=territory,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
        role=role,
        purpose_expires_at=expires,
    )


def test_analyst_can_read_fiscal_content() -> None:
    _context(Role.ANALYST).ensure_fiscal_read()


def test_tech_admin_cannot_read_fiscal_content() -> None:
    try:
        _context(Role.TECH_ADMIN).ensure_fiscal_read()
    except ForbiddenError as exc:
        assert "fiscal" in exc.detail.lower()
    else:
        raise AssertionError("expected ForbiddenError")


def test_expired_purpose_is_rejected() -> None:
    expired = datetime(2020, 1, 1, tzinfo=UTC)
    try:
        _context(expires=expired).ensure_purpose_active(datetime.now(UTC))
    except ForbiddenError as exc:
        assert "purpose" in exc.detail.lower()
    else:
        raise AssertionError("expected ForbiddenError")


def test_denied_territory_is_rejected() -> None:
    try:
        _context(territory=TERRITORY_ALPHA_NORTE).ensure_territory_allowed({TERRITORY_ALPHA_CENTRO})
    except ForbiddenError as exc:
        assert "territory" in exc.detail.lower()
    else:
        raise AssertionError("expected ForbiddenError")


def test_cross_tenant_resource_is_not_visible() -> None:
    try:
        _context().ensure_same_tenant(TENANT_BETA)
    except NotVisibleError:
        return
    raise AssertionError("expected NotVisibleError")
