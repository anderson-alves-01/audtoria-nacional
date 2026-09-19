"""Synthetic local seed moved out of migrations.

Revision ID: 0003_f0_synthetic_seed
Revises: 0002_f0_identity
Create Date: 2026-09-18
"""

revision = "0003_f0_synthetic_seed"
down_revision = "0002_f0_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Mutable synthetic data is loaded by sirta_api.adapters.db.seed."""


def downgrade() -> None:
    pass
