"""F3.1 catalog-driven synthetic source ingest. Schema-only version bump.

Revision ID: 0013_source_ingest
Revises: 0012_program_gates
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0013_source_ingest"
down_revision = "0012_program_gates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.11' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = 'F3_SOURCE_INGEST_LOCAL' WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    pass
