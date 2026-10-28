from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.tax_rates import list_tax_rates
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.get("/v1/tax-rates")
def get_tax_rates(
    tax: str | None = Query(None),
    uf: str | None = Query(None),
    on: str | None = Query(None),
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return list_tax_rates(session, context=context, tax=tax, uf=uf, on=on)
