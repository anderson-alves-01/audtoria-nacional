from sqlalchemy.orm import Session

from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.dlp import DlpResult, scan_prompt


def scan_prompt_for_ai(text: str) -> DlpResult:
    """Application wrapper so callers never bypass domain DLP."""
    return scan_prompt(text)


def record_tool_call_audit(
    session: Session,
    *,
    context: AccessContext,
    tool_name: str,
    route: str,
    outcome: str,
) -> None:
    """Immutable audit for privileged tool invocations (prefix tool.)."""
    record_audit(
        session,
        context=context,
        action=f"tool.{tool_name}",
        route=route,
        outcome=outcome,
        resource_type="tool_call",
        resource_id=None,
    )
