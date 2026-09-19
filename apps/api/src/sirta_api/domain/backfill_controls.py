"""Fail-closed controls for partitioned official backfills."""

from __future__ import annotations

import shutil
from pathlib import Path

from sirta_api.domain.errors import ConflictError


def clamp_max_entes(requested: int, *, hard_cap: int) -> int:
    value = int(requested) if int(requested) > 0 else 1
    cap = int(hard_cap) if int(hard_cap) > 0 else 1
    if value > cap:
        raise ConflictError(
            f"max_entes_per_run {value} exceeds official hard_cap {cap}; "
            "national unlimited backfill is forbidden"
        )
    return value


def statement_partition_key(*, competence: str, query: dict) -> str:
    exercise = str(query.get("an_exercicio") or competence or "current")
    period = query.get("nr_periodo")
    if period not in (None, ""):
        return f"{exercise}:{period}"
    return exercise


def select_entes_slice(
    codes: list[str], *, skip: int, max_entes: int
) -> tuple[list[str], int, bool]:
    total = len(codes)
    if skip >= total:
        return [], skip, True
    selected = codes[skip : skip + max_entes]
    return selected, skip, False


def checkpoint_status_after_slice(*, next_offset: int, total_entes: int) -> str:
    if total_entes <= 0:
        return "COMPLETE"
    if next_offset >= total_entes:
        return "COMPLETE"
    return "IN_PROGRESS"


def build_backfill_metrics(
    *,
    offset: int,
    last_ente: str | None,
    entes_this_run: int,
    item_count: int,
    duration_ms: int,
    bytes_fetched: int,
    disk_free_bytes: int | None,
    total_entes: int,
    max_entes_per_run: int,
) -> dict:
    remaining = max(total_entes - offset, 0)
    return {
        "offset": offset,
        "lastEnte": last_ente,
        "entesThisRun": entes_this_run,
        "itemCount": item_count,
        "durationMs": duration_ms,
        "bytesFetched": bytes_fetched,
        "diskFreeBytes": disk_free_bytes,
        "totalEntes": total_entes,
        "remainingEntes": remaining,
        "maxEntesPerRun": max_entes_per_run,
    }


def assert_datalake_space(
    *, root: Path, min_free_bytes: int, required_bytes: int = 0
) -> int:
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    free = int(shutil.disk_usage(path).free)
    needed = max(int(min_free_bytes), int(required_bytes))
    if free < needed:
        raise ConflictError(
            f"insufficient datalake disk space: free={free} required={needed}"
        )
    return free


def resolve_fpm_endpoint(catalog: dict) -> str:
    parameters = catalog.get("parameters") or {}
    by_competence = parameters.get("resource_url_by_competence") or {}
    competence = str(
        parameters.get("competence") or catalog.get("competence") or ""
    )
    if competence and isinstance(by_competence, dict):
        mapped = by_competence.get(competence)
        if mapped:
            return str(mapped)
    return str(catalog.get("endpoint") or "")
