from fastapi import APIRouter, Request

from sirta_api.adapters.health import ping_database
from sirta_api.adapters.http.problem import problem_response
from sirta_api.config import get_settings

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    config = get_settings()
    return {
        "status": "ok",
        "specVersion": config.spec_version,
        "implementationVersion": config.implementation_version,
        "releaseStage": config.release_stage,
    }


@router.get("/ready")
def ready(request: Request):
    config = get_settings()
    trace_id = getattr(request.state, "trace_id", "untraced")
    try:
        ping_database(config.database_url)
    except Exception:
        return problem_response(
            status=503,
            title="Service Unavailable",
            code="not-ready",
            detail="Database is unavailable",
            trace_id=trace_id,
        )
    return {
        "status": "ready",
        "specVersion": config.spec_version,
        "implementationVersion": config.implementation_version,
        "releaseStage": config.release_stage,
    }
