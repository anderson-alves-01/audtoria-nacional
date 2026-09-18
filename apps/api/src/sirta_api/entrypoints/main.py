from fastapi import FastAPI

from sirta_api.adapters.http.logging import TraceMiddleware, configure_logging
from sirta_api.entrypoints.health import router as health_router


def create_app() -> FastAPI:
    configure_logging()
    application = FastAPI(
        title="SIRTA Municipal API",
        version="0.3.1",
    )
    application.add_middleware(TraceMiddleware)
    application.include_router(health_router)
    return application


app = create_app()
