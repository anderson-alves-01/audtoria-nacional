from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from sirta_api.adapters.http.logging import TraceMiddleware, configure_logging
from sirta_api.adapters.http.problem import problem_response
from sirta_api.domain.errors import ProblemError
from sirta_api.entrypoints.audit import router as audit_router
from sirta_api.entrypoints.health import router as health_router
from sirta_api.entrypoints.tax_credits import router as tax_credit_router


def create_app() -> FastAPI:
    configure_logging()
    application = FastAPI(
        title="SIRTA Municipal API",
        version="0.3.1",
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
