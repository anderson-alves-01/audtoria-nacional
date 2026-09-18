from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.gates import list_program_gates
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/program-gates")
def get_program_gates(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_program_gates(session, context=context)
