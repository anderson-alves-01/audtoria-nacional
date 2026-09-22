from pathlib import Path

import pytest

from sirta_api.application.public_open_session import mint_public_open_session
from sirta_api.config import Settings
from sirta_api.domain.errors import ForbiddenError


def test_public_open_session_requires_flag(db_session) -> None:
    settings = Settings(
        public_open_ui_bootstrap=False,
        oidc_signing_key_path="tests/fixtures/jwt/private.pem",
        oidc_jwks_path="tests/fixtures/jwt/jwks.json",
    )
    with pytest.raises(ForbiddenError):
        mint_public_open_session(db_session, settings=settings)


def test_public_open_session_mints_mfa_token(db_session) -> None:
    settings = Settings(
        public_open_ui_bootstrap=True,
        oidc_signing_key_path=str(Path("tests/fixtures/jwt/private.pem")),
        oidc_jwks_path=str(Path("tests/fixtures/jwt/jwks.json")),
        oidc_issuer="http://localhost:8081/realms/sirta",
        oidc_audience="sirta-api",
    )
    body = mint_public_open_session(db_session, settings=settings)
    assert body["accessToken"]
    assert body["createsTaxCredit"] is False
    assert body["mode"] == "PUBLIC_OPEN_UI_BOOTSTRAP"
    assert body["territoryId"]
    assert body["purposeId"]
