from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.http.deps import get_access_context
from sirta_api.application.pipeline import (
    execute_synthetic_iss_load,
    published_funnel,
    rollback_gold,
)
from sirta_api.domain.authorization import AccessContext

router = APIRouter()


@router.post("/v1/data-loads/synthetic-iss")
def run_synthetic_iss(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
    dry_run: bool = Query(False),
) -> dict:
    return execute_synthetic_iss_load(session, context=context, dry_run=dry_run)


@router.post("/v1/data-loads/{run_id}/rollback")
def rollback_load(
    run_id: UUID,
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return rollback_gold(session, context=context, run_id=run_id)


@router.get("/v1/indicators/credit-funnel")
def credit_funnel(
    context: AccessContext = Depends(get_access_context),
    session: Session = Depends(get_session),
) -> dict:
    return published_funnel(session, context=context)
