"""G8 IBS/CBS synthetic non-binding calendar.

Revision ID: 0009_g8_regulatory
Revises: 0008_g7_transfers
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0009_g8_regulatory"
down_revision = "0008_g7_transfers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.7' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'G8_IBS_CBS_LOCAL' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
