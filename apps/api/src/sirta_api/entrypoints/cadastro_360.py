from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.cadastro_360 import (
    cadastro_360_command_rejected,
    get_cadastro_360,
)
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/cadastro-360")
def cadastro_360_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> dict:
    return get_cadastro_360(session, context=context, page=page, size=size)


@router.post("/v1/cadastro-360")
def cadastro_360_command_endpoint(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> None:
    cadastro_360_command_rejected(session, context=context)
