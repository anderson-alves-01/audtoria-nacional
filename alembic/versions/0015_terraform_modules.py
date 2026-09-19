"""Terraform documentation modules. Schema-only version bump.

Revision ID: 0015_terraform_modules
Revises: 0014_tesouro_stub_gates
Create Date: 2026-09-18
"""

from alembic import op

from sirta_api.adapters.db.models import Base

revision = "0015_terraform_modules"
down_revision = "0014_tesouro_stub_gates"
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())
    op.execute("UPDATE schema_meta SET value = '0.3.13' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = 'TERRAFORM_MODULES_DOCS' WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    pass
