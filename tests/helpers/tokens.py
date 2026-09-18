from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import jwt

from sirta_api.adapters.db.synthetic_ids import AUDIENCE, ISSUER

PRIVATE_KEY = Path("tests/fixtures/jwt/private.pem").read_bytes()


def issue_token(*, subject: UUID, tenant_id: UUID, expires_in: int = 3600) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "tenant_id": str(tenant_id),
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256", headers={"kid": "sirta-test"})


def auth_headers(
    *,
    subject: UUID,
    tenant_id: UUID,
    territory_id: UUID,
    purpose_id: UUID,
) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {issue_token(subject=subject, tenant_id=tenant_id)}",
        "X-Territory-Id": str(territory_id),
        "X-Purpose-Id": str(purpose_id),
    }
