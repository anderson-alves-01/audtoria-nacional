from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import Evidence
from sirta_api.adapters.db.synthetic_ids import (
    EVIDENCE_ALPHA,
    EVIDENCE_ALPHA_SHA256,
    EVIDENCE_BETA,
    TENANT_ALPHA,
    TENANT_BETA,
)


def test_synthetic_evidence_persists_sha256(db_session: Session) -> None:
    alpha = db_session.get(Evidence, EVIDENCE_ALPHA)
    assert alpha is not None
    assert alpha.tenant_id == TENANT_ALPHA
    assert alpha.sha256 == EVIDENCE_ALPHA_SHA256
    assert len(alpha.sha256) == 64
    beta = db_session.get(Evidence, EVIDENCE_BETA)
    assert beta is not None
    assert beta.tenant_id == TENANT_BETA
    rows = db_session.scalars(select(Evidence)).all()
    assert {row.id for row in rows} == {EVIDENCE_ALPHA, EVIDENCE_BETA}
