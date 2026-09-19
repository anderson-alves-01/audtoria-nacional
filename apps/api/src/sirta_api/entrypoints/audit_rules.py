from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.audit_rules import list_audit_rules
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/audit-rules")
def audit_rules_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_audit_rules(session, context=context)
