"""Store a password hash and an authenticator secret. Values stay out of the catalog.

Revision ID: 0107_user_login_secret
Revises: 0106_user_access_active
Create Date: 2026-10-08
"""

import sqlalchemy as sa
from alembic import op

revision = "0107_user_login_secret"
down_revision = "0106_user_access_active"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=256), nullable=True))
    op.add_column("users", sa.Column("totp_secret", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "totp_secret")
    op.drop_column("users", "password_hash")
