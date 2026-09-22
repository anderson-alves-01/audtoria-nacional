from __future__ import annotations

import structlog

logger = structlog.get_logger("sirta.ingest")


def log_ingest_started(
    *,
    source_id: str,
    tenant_id: str,
    territory_id: str,
    job_id: str | None = None,
) -> None:
    logger.info(
        "ingest_started",
        source_id=source_id,
        tenant_id=tenant_id,
        territory_id=territory_id,
        job_id=job_id,
    )


def log_ingest_finished(
    *,
    outcome: str,
    source_id: str,
    tenant_id: str,
    territory_id: str,
    run_id: str | None,
    received_count: int,
    silver_count: int,
    quarantined_count: int,
    job_id: str | None = None,
    error: str | None = None,
    http_status: int | None = None,
) -> None:
    payload: dict = {
        "outcome": outcome,
        "source_id": source_id,
        "tenant_id": tenant_id,
        "territory_id": territory_id,
        "run_id": run_id,
        "received_count": received_count,
        "silver_count": silver_count,
        "quarantined_count": quarantined_count,
        "job_id": job_id,
    }
    if error:
        payload["error"] = error
    if http_status is not None:
        payload["http_status"] = http_status
    logger.info("ingest_finished", **payload)
