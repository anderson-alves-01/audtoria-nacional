"""G6 finance states for payment, installment and active debt.

Revision ID: 0007_g6_finance
Revises: 0006_s4_pipeline
Create Date: 2026-09-18
"""

from alembic import op
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import Base, User, UserTerritory
from sirta_api.adapters.db.synthetic_ids import (
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_DEBT_ALPHA,
)

revision = "0007_g6_finance"
down_revision = "0006_s4_pipeline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    session = Session(bind=bind)
    if session.get(User, USER_DEBT_ALPHA) is None:
        session.add(
            User(
                id=USER_DEBT_ALPHA,
                tenant_id=TENANT_ALPHA,
                subject=str(USER_DEBT_ALPHA),
                username="debt.alpha",
                role="debt_officer",
            )
        )
        session.flush()
        session.add(UserTerritory(user_id=USER_DEBT_ALPHA, territory_id=TERRITORY_ALPHA_CENTRO))
        session.flush()
    op.execute("UPDATE schema_meta SET value = '0.3.5' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'G6_FINANCE' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
