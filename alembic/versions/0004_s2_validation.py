"""Sprint 2 validation schema. Seed is not applied here.

Revision ID: 0004_s2_validation
Revises: 0003_f0_synthetic_seed
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0004_s2_validation"
down_revision = "0003_f0_synthetic_seed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.2' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'S2_CREDIT_VALIDATION' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
