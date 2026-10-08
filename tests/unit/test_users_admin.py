from uuid import uuid4

import pytest

from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import ForbiddenError, ValidationFailedError
from sirta_api.domain.identities import Role
from sirta_api.domain.users_admin import keeps_last_technical_admin, user_draft


def test_draft_rejects_a_password_and_a_foreign_territory():
    territory = uuid4()
    with pytest.raises(ValidationFailedError):
        user_draft(
            {"username": "ana", "role": "analyst", "password": "x"},
            allowed_territories={territory},
        )
    with pytest.raises(ValidationFailedError):
        user_draft(
            {"username": "ana", "role": "analyst", "territoryIds": [str(uuid4())]},
            allowed_territories={territory},
        )


def test_draft_keeps_role_and_territory_without_a_secret():
    territory = uuid4()
    draft = user_draft(
        {"username": "ana", "role": "analyst", "territoryIds": [str(territory)]},
        allowed_territories={territory},
    )
    assert draft["role"] == "analyst"
    assert draft["territoryIds"] == [territory]
    assert "password" not in draft


def test_public_session_and_analyst_cannot_manage_users():
    public = _context(Role.TECH_ADMIN, "PUBLIC_OPEN_UI_BOOTSTRAP")
    analyst = _context(Role.ANALYST, "")
    admin = _context(Role.TECH_ADMIN, "")
    with pytest.raises(ForbiddenError):
        public.ensure_can_manage_users()
    with pytest.raises(ForbiddenError):
        analyst.ensure_can_manage_users()
    admin.ensure_can_manage_users()


def test_last_technical_admin_stays_active():
    with pytest.raises(ValidationFailedError):
        keeps_last_technical_admin(is_last=True, next_role="analyst", active=True)
    keeps_last_technical_admin(is_last=False, next_role="analyst", active=False)


def _context(role: Role, mode: str) -> AccessContext:
    return AccessContext(
        user_id=uuid4(),
        tenant_id=uuid4(),
        territory_id=uuid4(),
        purpose_id=uuid4(),
        role=role,
        purpose_expires_at=None,
        session_mode=mode,
    )
