from uuid import uuid4

import pytest

from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import UnauthorizedError, ValidationFailedError
from sirta_api.domain.identities import Role
from sirta_api.domain.local_login import SESSION_MODE, _totp, confirm_login, hash_password


def test_short_password_is_refused_and_a_match_confirms_the_code():
    with pytest.raises(ValidationFailedError):
        hash_password("curta")
    stored = hash_password("senha-admin-12")
    secret = "JBSWY3DPEHPK3PXP"
    now = 1_700_000_000
    code = _totp(secret, now)
    assert confirm_login(
        active=True,
        password_hash=stored,
        totp_secret=secret,
        password="senha-admin-12",
        code=code,
        now=now,
    )
    with pytest.raises(UnauthorizedError):
        confirm_login(
            active=True,
            password_hash=stored,
            totp_secret=secret,
            password="senha-admin-12",
            code="000000",
            now=now,
        )


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


def test_totp_window_rejects_an_old_code():
    secret = "JBSWY3DPEHPK3PXP"
    now = 1_700_000_120
    old = _totp(secret, now - 120)
    stored = hash_password("senha-admin-12")
    with pytest.raises(UnauthorizedError):
        confirm_login(
            active=True,
            password_hash=stored,
            totp_secret=secret,
            password="senha-admin-12",
            code=old,
            now=now,
        )
