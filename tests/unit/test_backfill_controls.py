"""Controlled backfill safety for FPM / SICONFI statements."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sirta_api.domain.backfill_controls import (
    assert_datalake_space,
    build_backfill_metrics,
    checkpoint_status_after_slice,
    clamp_max_entes,
    resolve_fpm_endpoint,
    select_entes_slice,
    statement_partition_key,
)
from sirta_api.domain.errors import ConflictError


def test_clamp_max_entes_rejects_above_hard_cap() -> None:
    with pytest.raises(ConflictError, match="hard_cap"):
        clamp_max_entes(100, hard_cap=25)


def test_clamp_max_entes_applies_requested_within_cap() -> None:
    assert clamp_max_entes(5, hard_cap=25) == 5
    assert clamp_max_entes(0, hard_cap=25) == 1


def test_statement_partition_key_includes_period_when_present() -> None:
    assert (
        statement_partition_key(
            competence="2025",
            query={"an_exercicio": "2025", "nr_periodo": "6"},
        )
        == "2025:6"
    )
    assert (
        statement_partition_key(competence="2024", query={"an_exercicio": "2024"}) == "2024"
    )


def test_select_entes_slice_does_not_wrap_when_exhausted() -> None:
    codes = ["1100015", "1100023", "1100031"]
    selected, skip, exhausted = select_entes_slice(codes, skip=3, max_entes=2)
    assert selected == []
    assert skip == 3
    assert exhausted is True


def test_select_entes_slice_returns_window() -> None:
    codes = ["1100015", "1100023", "1100031"]
    selected, skip, exhausted = select_entes_slice(codes, skip=0, max_entes=2)
    assert selected == ["1100015", "1100023"]
    assert skip == 0
    assert exhausted is False


def test_checkpoint_status_complete_when_cursor_covers_all() -> None:
    assert checkpoint_status_after_slice(next_offset=3, total_entes=3) == "COMPLETE"
    assert checkpoint_status_after_slice(next_offset=2, total_entes=3) == "IN_PROGRESS"


def test_build_backfill_metrics_includes_volume_fields() -> None:
    metrics = build_backfill_metrics(
        offset=2,
        last_ente="1100023",
        entes_this_run=2,
        item_count=10,
        duration_ms=42,
        bytes_fetched=1024,
        disk_free_bytes=5_000_000_000,
        total_entes=3,
        max_entes_per_run=2,
    )
    assert metrics["remainingEntes"] == 1
    assert metrics["durationMs"] == 42
    assert metrics["bytesFetched"] == 1024
    assert metrics["diskFreeBytes"] == 5_000_000_000
    assert metrics["totalEntes"] == 3
    assert metrics["maxEntesPerRun"] == 2


def test_assert_datalake_space_fails_closed_when_insufficient() -> None:
    usage = MagicMock(free=100)
    with patch("sirta_api.domain.backfill_controls.shutil.disk_usage", return_value=usage):
        with pytest.raises(ConflictError, match="disk"):
            assert_datalake_space(root=Path("var/datalake"), min_free_bytes=1_000, required_bytes=50)


def test_assert_datalake_space_passes_when_enough() -> None:
    usage = MagicMock(free=10_000)
    with patch("sirta_api.domain.backfill_controls.shutil.disk_usage", return_value=usage):
        free = assert_datalake_space(
            root=Path("var/datalake"), min_free_bytes=1_000, required_bytes=50
        )
    assert free == 10_000


def test_resolve_fpm_endpoint_uses_competence_map() -> None:
    catalog = {
        "endpoint": "https://example.gov.br/default.csv",
        "parameters": {
            "competence": "2026-07",
            "resource_url_by_competence": {
                "2026-07": "https://example.gov.br/202607.csv",
                "2026-08": "https://example.gov.br/202608.csv",
            },
        },
    }
    assert resolve_fpm_endpoint(catalog) == "https://example.gov.br/202607.csv"


def test_resolve_fpm_endpoint_falls_back_to_endpoint() -> None:
    catalog = {"endpoint": "https://example.gov.br/default.csv", "parameters": {}}
    assert resolve_fpm_endpoint(catalog) == "https://example.gov.br/default.csv"
