"""G7 transfer occurrences. Never creates tax credits.

Revision ID: 0008_g7_transfers
Revises: 0007_g6_finance
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0008_g7_transfers"
down_revision = "0007_g6_finance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.6' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'G7_TRANSFERS' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
