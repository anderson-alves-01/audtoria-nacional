from fastapi import APIRouter

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
