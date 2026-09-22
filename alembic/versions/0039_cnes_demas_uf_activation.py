"""Record CNES DEMAS UF-scoped activation.

Revision ID: 0039_cnes_demas_uf_activation
Revises: 0038_anatel_meu_municipio
Create Date: 2026-09-19
"""

from alembic import op

revision = "0039_cnes_demas_uf_activation"
down_revision = "0038_anatel_meu_municipio"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.36' WHERE key = 'implementation_version'")
    op.execute(
        "UPDATE schema_meta SET value = "
        "'OFFICIAL_DATA_WAVE_1_COMPLETE_ROADMAP_IN_PROGRESS' "
        "WHERE key = 'release_stage'"
    )


def downgrade() -> None:
    op.execute("UPDATE schema_meta SET value = '0.3.35' WHERE key = 'implementation_version'")
