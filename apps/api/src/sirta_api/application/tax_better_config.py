"""Operator configuration for Tax Better intake. No outbound organ call."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from sirta_api.adapters.db.models import TaxBetterIntakeLine, TaxBetterSourceConfig
from sirta_api.adapters.ingest.catalog_loader import catalog_source
from sirta_api.application.audit import record_audit
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.errors import NotVisibleError, ValidationFailedError
from sirta_api.domain.tax_better import (
    IntakeConfigError,
    fgo_code,
    fgo_label,
    read_configured_intake,
    vision_from_stored,
)

CONNECTOR = "tax_better_intake"


def list_tax_better_vision(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    stored = session.scalars(
        select(TaxBetterIntakeLine)
        .where(
            TaxBetterIntakeLine.tenant_id == context.tenant_id,
            TaxBetterIntakeLine.territory_id == context.territory_id,
        )
        .order_by(TaxBetterIntakeLine.created_at)
    ).all()
    lines = [
        {
            "organ": row.organ,
            "tax": row.tax,
            "fgo": fgo_label(row.fgo_code),
            "competence": row.competence,
            "variables": dict(row.variables or {}),
            "operationValue": row.operation_value,
            "operationBase": row.operation_base,
            "operationTax": row.operation_tax,
            "malhaValue": row.malha_value,
            "malhaBase": row.malha_base,
            "malhaTax": row.malha_tax,
        }
        for row in stored
    ]
    try:
        view = vision_from_stored(lines)
    except (IntakeConfigError, ValueError) as exc:
        raise ValidationFailedError(str(exc)) from exc
    record_audit(
        session,
        context=context,
        action="tax_better_vision_read",
        route="/v1/tax-better/vision",
        outcome="success",
        resource_type="tax_better_intake",
    )
    return view


def get_tax_better_config(session: Session, *, context: AccessContext, source_id: str) -> dict:
    context.ensure_fiscal_read()
    _assert_source(source_id)
    row = _find(session, context, source_id)
    if row is None:
        return _public(source_id, None)
    return _public(source_id, row)


def save_tax_better_config(
    session: Session,
    *,
    context: AccessContext,
    source_id: str,
    payload: dict,
) -> dict:
    context.ensure_fiscal_write()
    _assert_source(source_id)
    _reject_secret_value(payload)
    config = _config_from(payload)
    _validate(config)
    row = _find(session, context, source_id)
    now = datetime.now(UTC)
    if row is None:
        row = TaxBetterSourceConfig(
            id=uuid4(),
            tenant_id=context.tenant_id,
            territory_id=context.territory_id,
            source_id=source_id,
            channel=config["channel"],
            field_map=config["fieldMap"],
            endpoint=config["endpoint"],
            secret_name=config["secretName"],
            updated_at=now,
        )
        session.add(row)
    else:
        row.channel = config["channel"]
        row.field_map = config["fieldMap"]
        row.endpoint = config["endpoint"]
        row.secret_name = config["secretName"]
        row.updated_at = now
    record_audit(
        session,
        context=context,
        action="tax_better_config_saved",
        route=f"/v1/data-sources/{source_id}/tax-better-config",
        outcome="success",
        resource_type="tax_better_source_config",
        resource_id=row.id,
    )
    session.flush()
    return _public(source_id, row)


def stage_tax_better_intake(
    session: Session,
    *,
    context: AccessContext,
    source_id: str,
    payload: dict,
) -> dict:
    context.ensure_fiscal_write()
    _assert_source(source_id)
    row = _find(session, context, source_id)
    if row is None:
        raise ValidationFailedError("Leiaute incompleto: grave o canal e o mapa de campos.")
    config = _config_from_row(row)
    try:
        result = read_configured_intake(
            config,
            file_text=payload.get("fileText"),
            api_rows=payload.get("rows"),
        )
    except IntakeConfigError as exc:
        raise ValidationFailedError(str(exc)) from exc
    now = datetime.now(UTC)
    for line in result["accepted"]:
        session.add(
            TaxBetterIntakeLine(
                id=uuid4(),
                tenant_id=context.tenant_id,
                territory_id=context.territory_id,
                organ=line["organ"],
                tax=line["tax"],
                fgo_code=fgo_code(line["fgo"]),
                variables=line["variables"],
                competence=payload.get("competence"),
                operation_value=line["operationValue"],
                operation_base=line["operationBase"],
                operation_tax=line["operationTax"],
                malha_value=line["malhaValue"],
                malha_base=line["malhaBase"],
                malha_tax=line["malhaTax"],
                approved=False,
                created_at=now,
            )
        )
    record_audit(
        session,
        context=context,
        action="tax_better_intake_staged",
        route=f"/v1/data-sources/{source_id}/tax-better-intake",
        outcome="success",
        resource_type="tax_better_intake",
    )
    session.flush()
    return {
        "sourceId": source_id,
        "createsTaxCredit": False,
        "acceptedCount": len(result["accepted"]),
        "quarantinedCount": len(result["quarantined"]),
        "quarantined": result["quarantined"],
        "vision": result["vision"],
    }


def _assert_source(source_id: str) -> None:
    item = catalog_source(source_id)
    if item is None or item.get("connector") != CONNECTOR:
        raise NotVisibleError("Fonte Tax Better não encontrada.")


def _reject_secret_value(payload: dict) -> None:
    if "secret" in payload or "secretValue" in payload:
        raise ValidationFailedError("O segredo não é gravado. Informe só o nome.")


def _validate(config: dict) -> None:
    try:
        if config["channel"] == "api":
            read_configured_intake(config, api_rows=[])
        else:
            read_configured_intake(config, file_text="")
    except IntakeConfigError as exc:
        raise ValidationFailedError(str(exc)) from exc


def _config_from(payload: dict) -> dict:
    return {
        "channel": payload.get("channel"),
        "fieldMap": dict(payload.get("fieldMap") or {}),
        "endpoint": str(payload.get("endpoint") or ""),
        "secretName": str(payload.get("secretName") or ""),
    }


def _config_from_row(row: TaxBetterSourceConfig) -> dict:
    return {
        "channel": row.channel,
        "fieldMap": dict(row.field_map or {}),
        "endpoint": row.endpoint,
        "secretName": row.secret_name,
    }


def _find(session: Session, context: AccessContext, source_id: str) -> TaxBetterSourceConfig | None:
    return session.scalar(
        select(TaxBetterSourceConfig).where(
            TaxBetterSourceConfig.tenant_id == context.tenant_id,
            TaxBetterSourceConfig.territory_id == context.territory_id,
            TaxBetterSourceConfig.source_id == source_id,
        )
    )


def _public(source_id: str, row: TaxBetterSourceConfig | None) -> dict:
    if row is None:
        return {
            "sourceId": source_id,
            "channel": "",
            "fieldMap": {},
            "endpoint": "",
            "secretName": "",
            "createsTaxCredit": False,
        }
    return {
        "sourceId": source_id,
        "channel": row.channel,
        "fieldMap": row.field_map,
        "endpoint": row.endpoint,
        "secretName": row.secret_name,
        "createsTaxCredit": False,
    }
