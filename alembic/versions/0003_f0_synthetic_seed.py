"""Synthetic local seed. Never used with real municipal data.

Revision ID: 0003_f0_synthetic_seed
Revises: 0002_f0_identity
Create Date: 2026-09-18
"""

from alembic import op
from sqlalchemy.orm import Session

from sirta_api.adapters.db.seed import seed_synthetic

revision = "0003_f0_synthetic_seed"
down_revision = "0002_f0_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    session = Session(bind=op.get_bind())
    seed_synthetic(session)
    session.flush()


def downgrade() -> None:
    pass
