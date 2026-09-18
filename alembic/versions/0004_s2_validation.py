"""Sprint 2 validation tables and hashed synthetic evidence.

Revision ID: 0004_s2_validation
Revises: 0003_f0_synthetic_seed
Create Date: 2026-09-18
"""

from alembic import op
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import Base, Evidence
from sirta_api.adapters.db.synthetic_ids import (
    EVIDENCE_ALPHA,
    EVIDENCE_ALPHA_SHA256,
    EVIDENCE_BETA,
    EVIDENCE_BETA_SHA256,
    TENANT_ALPHA,
    TENANT_BETA,
)

revision = "0004_s2_validation"
down_revision = "0003_f0_synthetic_seed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    session = Session(bind=bind)
    if session.get(Evidence, EVIDENCE_ALPHA) is None:
        session.add(
            Evidence(
                id=EVIDENCE_ALPHA,
                tenant_id=TENANT_ALPHA,
                sha256=EVIDENCE_ALPHA_SHA256,
                source="synthetic-ledger",
                media_type="text/plain",
            )
        )
    if session.get(Evidence, EVIDENCE_BETA) is None:
        session.add(
            Evidence(
                id=EVIDENCE_BETA,
                tenant_id=TENANT_BETA,
                sha256=EVIDENCE_BETA_SHA256,
                source="synthetic-ledger",
                media_type="text/plain",
            )
        )
    session.flush()
    op.execute(
        "UPDATE schema_meta SET value = '0.3.2' WHERE key = 'implementation_version'"
    )
    op.execute(
        "UPDATE schema_meta SET value = 'S2_CREDIT_VALIDATION' WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    pass
