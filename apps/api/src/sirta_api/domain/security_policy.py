"""MFA policy for non-local environments. Local remains fail-closed on auth only."""

from __future__ import annotations

from typing import Any

from sirta_api.domain.errors import ForbiddenError

_MFA_ACR_MARKERS = ("mfa", "https://refeds.org/profile/mfa")


def token_has_mfa(claims: dict[str, Any]) -> bool:
    if claims.get("mfa") is True:
        return True
    amr = claims.get("amr")
    if isinstance(amr, str):
        amr = [amr]
    if isinstance(amr, list) and any(str(item).lower() == "mfa" for item in amr):
        return True
    acr = str(claims.get("acr") or "").lower()
    return any(marker in acr for marker in _MFA_ACR_MARKERS)


def ensure_mfa_if_required(claims: dict[str, Any], *, environment: str) -> None:
    if environment.strip().lower() in {"", "local"}:
        return
    if token_has_mfa(claims):
        return
    raise ForbiddenError("MFA is required outside the local environment; token lacks MFA evidence")
