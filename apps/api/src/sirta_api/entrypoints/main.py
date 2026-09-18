from fastapi import FastAPI

from sirta_api.entrypoints.health import router as health_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="SIRTA Municipal API",
        version="0.3.1",
    )
    application.include_router(health_router)
    return application


app = create_app()
