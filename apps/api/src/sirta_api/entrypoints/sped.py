from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.sped_ingest import ingest_sped_upload, list_sped_operations
from sirta_api.domain.authorization import AccessContext

router = APIRouter()

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.post("/v1/data-sources/{sourceId}/upload")
def post_source_upload(
    sourceId: str,
    body: bytes = Body(..., media_type=XLSX_MEDIA_TYPE),
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return ingest_sped_upload(session, context=context, source_id=sourceId, body=body)


@router.get("/v1/sped-operacoes")
def get_sped_operacoes(
    level: str = Query("SERIE"),
    ano: int | None = Query(None),
    uf: str | None = Query(None),
    operacao: str | None = Query(None),
    cfop: str | None = Query(None),
    page: int = Query(1),
    pageSize: int = Query(200),
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_sped_operations(
        session,
        context=context,
        level=level,
        ano=ano,
        uf=uf,
        operacao=operacao,
        cfop=cfop,
        page=page,
        page_size=pageSize,
    )
