from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.transfers import execute_create_transfer, list_transfers
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


class TransferIn(BaseModel):
    transferType: str
    competence: str
    officialSource: str
    expectedAmount: float | None = None
    receivedAmount: float = Field(ge=0)


@router.get("/v1/transfer-occurrences")
def get_transfers(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_transfers(session, context=context)


@router.post("/v1/transfer-occurrences", status_code=201)
def post_transfer(
    payload: TransferIn,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return execute_create_transfer(session, context=context, payload=payload.model_dump())
