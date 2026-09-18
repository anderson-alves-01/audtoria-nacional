"""Sprint 3 collection cases and collector identity.

Revision ID: 0005_s3_collection
Revises: 0004_s2_validation
Create Date: 2026-09-18
"""

from alembic import op
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import Base, User, UserTerritory
from sirta_api.adapters.db.synthetic_ids import (
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_COLLECTOR_ALPHA,
)

revision = "0005_s3_collection"
down_revision = "0004_s2_validation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    session = Session(bind=bind)
    if session.get(User, USER_COLLECTOR_ALPHA) is None:
        session.add(
            User(
                id=USER_COLLECTOR_ALPHA,
                tenant_id=TENANT_ALPHA,
                subject=str(USER_COLLECTOR_ALPHA),
                username="collector.alpha",
                role="collector",
            )
        )
        session.flush()
        session.add(
            UserTerritory(
                user_id=USER_COLLECTOR_ALPHA,
                territory_id=TERRITORY_ALPHA_CENTRO,
            )
        )
        session.flush()
    op.execute("UPDATE schema_meta SET value = '0.3.3' WHERE key = 'implementation_version'")
    op.execute("UPDATE schema_meta SET value = 'S3_COLLECTION' WHERE key = 'release_stage'")


def downgrade() -> None:
    pass
