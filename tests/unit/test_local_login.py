from uuid import uuid4

import pytest

from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import UnauthorizedError, ValidationFailedError
from sirta_api.domain.identities import Role
from sirta_api.domain.local_login import SESSION_MODE, confirm_login, hash_password


def test_short_password_is_refused_and_a_match_opens_the_session():
    with pytest.raises(ValidationFailedError):
        hash_password("curta")
    stored = hash_password("admin2026")
    assert confirm_login(active=True, password_hash=stored, password="admin2026")
    with pytest.raises(UnauthorizedError):
        confirm_login(active=True, password_hash=stored, password="outra-senha")


def test_operator_session_can_manage_users():
    context = AccessContext(
        user_id=uuid4(),
        tenant_id=uuid4(),
        territory_id=uuid4(),
        purpose_id=uuid4(),
        role=Role.TECH_ADMIN,
        purpose_expires_at=None,
        session_mode=SESSION_MODE,
    )
    context.ensure_can_manage_users()
