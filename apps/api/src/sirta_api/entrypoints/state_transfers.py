from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.state_transfers import (
    get_state_transfers,
    state_transfers_command_rejected,
)
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/state-transfers")
def state_transfers_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=30, ge=1, le=100),
) -> dict:
    return get_state_transfers(session, context=context, page=page, size=size)


@router.post("/v1/state-transfers")
def state_transfers_command_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> None:
    state_transfers_command_rejected(session, context=context)
