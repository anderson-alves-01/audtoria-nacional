from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.ops_governance import get_ops_governance
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/ops-governance")
def ops_governance_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return get_ops_governance(session, context=context)
