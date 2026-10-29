from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.cgu_nfe_series import list_cgu_nfe
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/cgu-nfe")
def get_cgu_nfe(
    uf: str | None = Query(None),
    ano: int | None = Query(None),
    page: int = Query(1),
    pageSize: int = Query(200),
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_cgu_nfe(
        session,
        context=context,
        uf=uf,
        ano=ano,
        page=page,
        page_size=pageSize,
    )
