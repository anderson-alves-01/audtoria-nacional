"""Program gates snapshot. Schema-only version bump.

Revision ID: 0012_program_gates
Revises: 0011_source_catalog
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0012_program_gates"
down_revision = "0011_source_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.10' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'PROGRAM_GATES_LOCAL' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
