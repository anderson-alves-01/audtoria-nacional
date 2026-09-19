"""Tesouro synthetic stub and G0/G1 blocked checklists. Schema-only version bump.

Revision ID: 0014_tesouro_stub_gates
Revises: 0013_source_ingest
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0014_tesouro_stub_gates"
down_revision = "0013_source_ingest"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.12' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = 'TESOURO_STUB_GATES_LOCAL' WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    pass
