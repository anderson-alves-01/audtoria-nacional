from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.transfer_reconciliation import (
    get_transfer_reconciliation,
    reconciliation_command_rejected,
)
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/transfer-reconciliation")
def transfer_reconciliation_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> dict:
    return get_transfer_reconciliation(session, context=context, page=page, size=size)


@router.post("/v1/transfer-reconciliation")
def transfer_reconciliation_command_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> None:
    reconciliation_command_rejected(session, context=context)
