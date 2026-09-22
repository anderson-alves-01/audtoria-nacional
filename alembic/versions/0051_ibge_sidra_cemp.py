"""Record IBGE SIDRA 9509 CEMP municipal activation.

Revision ID: 0051_ibge_sidra_cemp
Revises: 0050_state_pa_icms_verde
Create Date: 2026-09-20
"""

from alembic import op

revision = "0051_ibge_sidra_cemp"
down_revision = "0050_state_pa_icms_verde"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.48' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.47' WHERE key = 'implementation_version'")
