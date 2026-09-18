"""Alembic hygiene: schema_meta only. Synthetic seed remains outside migrations.

Revision ID: 0010_alembic_hygiene
Revises: 0009_g8_regulatory
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0010_alembic_hygiene"
down_revision = "0009_g8_regulatory"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.8' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'ALEMBIC_HYGIENE' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
