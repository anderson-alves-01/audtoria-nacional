from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import Tenant, User
from sirta_api.adapters.db.synthetic_ids import TENANT_ALPHA, TENANT_BETA, USER_ANALYST_ALPHA


def test_seed_persists_two_isolated_tenants(db_session: Session) -> None:
    tenants = db_session.scalars(select(Tenant)).all()
    assert {tenant.slug for tenant in tenants} == {"alpha", "beta"}
    user = db_session.get(User, USER_ANALYST_ALPHA)
    assert user is not None
    assert user.tenant_id == TENANT_ALPHA
    assert user.tenant_id != TENANT_BETA
