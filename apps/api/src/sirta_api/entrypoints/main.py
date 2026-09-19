from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from sirta_api.adapters.http.logging import TraceMiddleware, configure_logging
from sirta_api.adapters.http.problem import problem_response
from sirta_api.domain.errors import ProblemError
from sirta_api.entrypoints.active_debt_panel import router as active_debt_panel_router
from sirta_api.entrypoints.audit import router as audit_router
from sirta_api.entrypoints.audit_cases import router as audit_cases_router
from sirta_api.entrypoints.audit_rules import router as audit_rules_router
from sirta_api.entrypoints.cadastro_360 import router as cadastro_360_router
from sirta_api.entrypoints.catalog import router as catalog_router
from sirta_api.entrypoints.collection_panel import router as collection_panel_router
from sirta_api.entrypoints.dashboards import router as dashboard_router
from sirta_api.entrypoints.diagnosis import router as diagnosis_router
from sirta_api.entrypoints.findings import router as findings_router
from sirta_api.entrypoints.gates import router as gates_router
from sirta_api.entrypoints.health import router as health_router
from sirta_api.entrypoints.human_validation import router as human_validation_router
from sirta_api.entrypoints.municipal_uploads import router as municipal_uploads_router
from sirta_api.entrypoints.notifications import router as notifications_router
from sirta_api.entrypoints.ops_governance import router as ops_governance_router
from sirta_api.entrypoints.payments_panel import router as payments_panel_router
from sirta_api.entrypoints.pilot_readiness import router as pilot_readiness_router
from sirta_api.entrypoints.pipeline import router as pipeline_router
from sirta_api.entrypoints.procuradoria_panel import router as procuradoria_panel_router
from sirta_api.entrypoints.regulatory import router as regulatory_router
from sirta_api.entrypoints.sectoral_enrichment import router as sectoral_enrichment_router
from sirta_api.entrypoints.state_transfers import router as state_transfers_router
from sirta_api.entrypoints.tax_credits import router as tax_credit_router
from sirta_api.entrypoints.transfer_reconciliation import (
    router as transfer_reconciliation_router,
)
from sirta_api.entrypoints.transfers import router as transfer_router


def create_app() -> FastAPI:
    configure_logging()
    application = FastAPI(
        title="SIRTA Municipal API",
        version="0.3.26",
    )
    application.add_middleware(TraceMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(tax_credit_router)
    application.include_router(pipeline_router)
    application.include_router(transfer_router)
    application.include_router(regulatory_router)
    application.include_router(diagnosis_router)
    application.include_router(audit_rules_router)
    application.include_router(findings_router)
    application.include_router(audit_cases_router)
    application.include_router(human_validation_router)
    application.include_router(notifications_router)
    application.include_router(collection_panel_router)
    application.include_router(payments_panel_router)
    application.include_router(active_debt_panel_router)
    application.include_router(procuradoria_panel_router)
    application.include_router(transfer_reconciliation_router)
    application.include_router(pilot_readiness_router)
    application.include_router(ops_governance_router)
    application.include_router(municipal_uploads_router)
    application.include_router(cadastro_360_router)
    application.include_router(sectoral_enrichment_router)
    application.include_router(state_transfers_router)
    application.include_router(catalog_router)
    application.include_router(dashboard_router)
    application.include_router(gates_router)
    application.include_router(audit_router)

    @application.exception_handler(ProblemError)
    async def problem_handler(request: Request, exc: ProblemError):
        trace_id = getattr(request.state, "trace_id", "untraced")
        return problem_response(
            status=exc.status,
            title=exc.title,
            code=exc.code,
            detail=exc.detail,
            trace_id=trace_id,
        )

    return application


app = create_app()
