from sirta_api.adapters.http.logging import configure_logging
from sirta_api.adapters.observability.ingest_events import (
    log_ingest_finished,
    log_ingest_started,
)


def test_ingest_observability_emits_run_id_and_volumes(capsys) -> None:
    configure_logging()
    log_ingest_started(
        source_id="IBGE-SIDRA",
        tenant_id="tenant-alpha",
        territory_id="territory-alpha",
        job_id="job-1",
    )
    log_ingest_finished(
        outcome="success",
        source_id="IBGE-SIDRA",
        tenant_id="tenant-alpha",
        territory_id="territory-alpha",
        run_id="run-123",
        received_count=10,
        silver_count=9,
        quarantined_count=1,
        job_id="job-1",
    )
    captured = capsys.readouterr().out
    assert "ingest_started" in captured
    assert "ingest_finished" in captured
    assert "run-123" in captured
    assert "IBGE-SIDRA" in captured
    assert "silver_count" in captured or '"silver_count": 9' in captured


def test_ingest_observability_failure_path_has_no_run_id(capsys) -> None:
    configure_logging()
    log_ingest_finished(
        outcome="unavailable",
        source_id="TESOURO-FPM-VALORES",
        tenant_id="tenant-alpha",
        territory_id="territory-alpha",
        run_id=None,
        received_count=0,
        silver_count=0,
        quarantined_count=0,
        error="connection reset",
    )
    captured = capsys.readouterr().out
    assert "ingest_finished" in captured
    assert "unavailable" in captured
    assert "connection reset" in captured
    assert "Bearer " not in captured
