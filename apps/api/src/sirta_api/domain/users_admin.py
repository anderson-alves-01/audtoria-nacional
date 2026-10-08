"""Rules for the user and access directory. No password is stored."""

from uuid import UUID

from sirta_api.domain.errors import ValidationFailedError
from sirta_api.domain.identities import Role

ROLE_LABELS = {
    Role.ANALYST.value: "Analista",
    Role.VALIDATOR.value: "Validador",
    Role.COLLECTOR.value: "Papel de cobrança",
    Role.DEBT_OFFICER.value: "Papel de dívida ativa",
    Role.TECH_ADMIN.value: "Administrador técnico",
}


def user_draft(payload: dict, *, allowed_territories: set[UUID]) -> dict:
    if any(key in payload for key in ("password", "secret", "secretValue")):
        raise ValidationFailedError("Senha não é gravada nesta tela.")
    username = str(payload.get("username") or "").strip()
    role = str(payload.get("role") or "").strip()
    raw_territories = payload.get("territoryIds") or []
    if not username or len(username) > 128:
        raise ValidationFailedError("Informe o nome do usuário.")
    if role not in ROLE_LABELS:
        raise ValidationFailedError("Papel não suportado.")
    if not isinstance(raw_territories, list) or not raw_territories:
        raise ValidationFailedError("Informe ao menos um território de acesso.")
    territories: list[UUID] = []
    for item in raw_territories:
        try:
            territory_id = UUID(str(item))
        except ValueError as exc:
            raise ValidationFailedError("Território de acesso inválido.") from exc
        if territory_id not in allowed_territories:
            raise ValidationFailedError("Território fora do tenant.")
        if territory_id not in territories:
            territories.append(territory_id)
    active = payload.get("active", True)
    if not isinstance(active, bool):
        raise ValidationFailedError("A situação do acesso precisa ser ativa ou inativa.")
    return {
        "username": username,
        "role": role,
        "territoryIds": territories,
        "active": active,
    }


def keeps_last_technical_admin(*, is_last: bool, next_role: str, active: bool) -> None:
    if is_last and (next_role != Role.TECH_ADMIN.value or not active):
        raise ValidationFailedError("O tenant precisa manter um administrador técnico ativo.")
