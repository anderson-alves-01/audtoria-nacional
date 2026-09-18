from typing import Any

from fastapi.responses import JSONResponse

PROBLEM_BASE = "https://auditoria-nacional.local/problems"


def problem_response(
    *,
    status: int,
    title: str,
    code: str,
    detail: str,
    trace_id: str,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "type": f"{PROBLEM_BASE}/{code}",
        "title": title,
        "status": status,
        "detail": detail,
        "traceId": trace_id,
    }
    return JSONResponse(
        status_code=status,
        content=payload,
        media_type="application/problem+json",
    )
