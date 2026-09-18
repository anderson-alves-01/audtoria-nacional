"""Identity, tax credit and audit tables for F0.

Revision ID: 0002_f0_identity
Revises: 0001_f0_schema_meta
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0002_f0_identity"
down_revision = "0001_f0_schema_meta"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
