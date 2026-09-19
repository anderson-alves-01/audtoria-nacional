from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.procuradoria_panel import (
    get_procuradoria_panel,
    legal_command_rejected,
)
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/procuradoria")
def procuradoria_panel_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return get_procuradoria_panel(session, context=context)


@router.post("/v1/procuradoria")
def procuradoria_command_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> None:
    legal_command_rejected(session, context=context)
