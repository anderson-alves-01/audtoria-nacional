"""Inventory, download with resume, circuit breaker and manual import. No real network."""

from pathlib import Path

import httpx
import pytest
from tests.helpers.cgu_nfe_synthetic import baseline_month

from sirta_api.adapters.ingest.cgu_nfe import acquire
from sirta_api.adapters.ingest.cgu_nfe.inventory import (
    CatalogUnavailable,
    fetch_catalog,
    month_statuses,
    parse_catalog,
    refresh_inventory,
)
from sirta_api.adapters.ingest.cgu_nfe.store import Store
from sirta_api.domain import cgu_nfe as d

WAF_PAGE = (
    b"<!DOCTYPE html><html><head><title>Human Verification</title></head>"
    b"<body>awsWafCookieDomainList</body></html>"
)
CATALOG = """<script>var arquivos = [];
arquivos.push({"ano" : "2021", "mes" : "04", "dia" : "", "origem" :  "NFe"});
arquivos.push({"ano" : "2024", "mes" : "01", "dia" : "", "origem" :  "NFe"});
arquivos.push({"ano" : "2024", "mes" : "02", "dia" : "", "origem" :  "NFe"});
arquivos.push({"ano" : "2024", "mes" : "03", "dia" : "", "origem" :  "OutraOrigem"});
</script>"""


@pytest.fixture
def store(tmp_path: Path):
    s = Store(tmp_path / "lake", run_id="test-run")
    yield s
    s.close()


@pytest.fixture
def zip_bytes(tmp_path: Path) -> bytes:
    path = tmp_path / "src" / "202401_NFe.zip"
    path.parent.mkdir()
    baseline_month(path)
    return path.read_bytes()


def client_for(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True)


def downloader(store, handler, **kwargs):
    waits: list[float] = []
    kwargs.setdefault("backoff", 1.0)
    dl = acquire.Downloader(store, client_for(handler), sleep=waits.append, **kwargs)
    return dl, waits


# -- catalog and inventory ---------------------------------------------------------------------
def test_parse_catalog_keeps_only_nfe_months() -> None:
    assert parse_catalog(CATALOG) == {"202104", "202401", "202402"}


def test_catalog_without_the_list_is_an_error_not_an_empty_inventory() -> None:
    client = client_for(lambda r: httpx.Response(200, text="<html>pagina alterada</html>"))
    with pytest.raises(CatalogUnavailable):
        fetch_catalog(client)
    client = client_for(lambda r: httpx.Response(405, content=WAF_PAGE))
    with pytest.raises(CatalogUnavailable, match="405"):
        fetch_catalog(client)


def test_inventory_states_and_head_probe(store: Store) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "catalogo" in request.url.path or "notas-fiscais" in request.url.path:
            return httpx.Response(200, text=CATALOG)
        if request.method == "HEAD" and request.url.path.endswith("202401_NFe.zip"):
            return httpx.Response(200, headers={"content-length": "123456"})
        return httpx.Response(403, text="<Error>AccessDenied</Error>")

    refresh_inventory(store, client_for(handler), probe=True)
    states = {s.month: s for s in month_statuses(store)}
    assert len(states) == 60
    assert states["202101"].state == d.STATE_NOT_LISTED
    assert states["202104"].state == d.STATE_PENDING
    assert states["202401"].head_size == 123456
    assert states["202402"].head_status == 403  # listed but HEAD refused: still only pending
    assert states["202402"].state == d.STATE_PENDING


def test_a_month_is_not_assumed_listed_before_the_catalog_was_read(store: Store) -> None:
    assert all(s.state == d.STATE_NOT_LISTED for s in month_statuses(store))


# -- download ---------------------------------------------------------------------------------
def test_download_validates_registers_and_is_idempotent(store: Store, zip_bytes: bytes) -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.method)
        return httpx.Response(200, content=zip_bytes)

    dl, waits = downloader(store, handler)
    first = dl.download_month("202401")
    assert first.outcome == acquire.OUTCOME_OK
    assert first.url == d.month_url("202401")
    assert store.bronze_path("202401").read_bytes() == zip_bytes
    assert not list(store.partial.glob("*.part"))
    row = store.current_file("202401")
    assert row["origem"] == "DOWNLOAD" and row["url_used"] == d.month_url("202401")
    assert row["run_id"] == "test-run"
    assert len(calls) == 1

    again = dl.download_month("202401")
    assert again.outcome == acquire.OUTCOME_ALREADY
    assert len(calls) == 1  # no second request
    assert waits == []


def test_download_resumes_from_a_partial_file(store: Store, zip_bytes: bytes) -> None:
    half = len(zip_bytes) // 2
    (store.partial / "202401_NFe.zip.part").write_bytes(zip_bytes[:half])
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["range"] = request.headers.get("range")
        total = len(zip_bytes)
        return httpx.Response(
            206,
            content=zip_bytes[half:],
            headers={"content-range": f"bytes {half}-{total - 1}/{total}"},
        )

    dl, _ = downloader(store, handler)
    result = dl.download_month("202401")
    assert seen["range"] == f"bytes={half}-"
    assert result.outcome == acquire.OUTCOME_OK
    assert store.bronze_path("202401").read_bytes() == zip_bytes


def test_download_restarts_when_the_server_ignores_range(store: Store, zip_bytes: bytes) -> None:
    (store.partial / "202401_NFe.zip.part").write_bytes(b"garbage-from-another-file")
    dl, _ = downloader(store, lambda r: httpx.Response(200, content=zip_bytes))
    assert dl.download_month("202401").outcome == acquire.OUTCOME_OK
    assert store.bronze_path("202401").read_bytes() == zip_bytes


def test_human_verification_wall_is_recorded_and_never_bypassed(store: Store) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(405, content=WAF_PAGE, headers={"content-type": "text/html"})

    dl, waits = downloader(store, handler)
    result = dl.download_month("202402")
    assert result.outcome == acquire.OUTCOME_BLOCKED
    assert result.http_status == 405
    assert len(seen) == 1  # no retry against the wall
    assert waits == []
    assert not store.bronze_path("202402").exists()
    assert "cookie" not in {k.lower() for k in seen[0].headers}  # no session tricks
    store.upsert_month("202402", url=d.month_url("202402"), listed=True)
    state = {s.month: s for s in month_statuses(store)}["202402"]
    assert state.state == d.STATE_BLOCKED
    assert "WAF" in state.detail


def test_html_with_status_200_is_not_accepted_as_a_zip(store: Store) -> None:
    dl, _ = downloader(store, lambda r: httpx.Response(200, content=WAF_PAGE))
    result = dl.download_month("202402")
    assert result.outcome == acquire.OUTCOME_BLOCKED
    assert not store.bronze_path("202402").exists()
    assert not list(store.partial.glob("*.part"))


def test_circuit_breaker_stops_after_repeated_blocks(store: Store) -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request.url.path)
        return httpx.Response(405, content=WAF_PAGE)

    dl, _ = downloader(store, handler, breaker_limit=2)
    months = ["202402", "202403", "202404", "202405", "202406"]
    results = dl.download_many(months, concurrency=1)
    outcomes = [r.outcome for r in results]
    assert outcomes == [acquire.OUTCOME_BLOCKED] * 2 + [acquire.OUTCOME_SKIPPED] * 3
    assert len(requests) == 2
    assert dl.breaker.is_open


def test_retries_with_progressive_wait_then_succeeds(store: Store, zip_bytes: bytes) -> None:
    answers = [httpx.Response(503), httpx.Response(503), httpx.Response(200, content=zip_bytes)]

    def handler(request: httpx.Request) -> httpx.Response:
        return answers.pop(0)

    dl, waits = downloader(store, handler, retries=4, backoff=1.5)
    result = dl.download_month("202401")
    assert result.outcome == acquire.OUTCOME_OK
    assert result.attempts == 3
    assert waits == [1.5, 3.0]


def test_network_failure_exhausts_limited_retries(store: Store) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timeout", request=request)

    dl, waits = downloader(store, handler, retries=3, backoff=1.0)
    result = dl.download_month("202401")
    assert result.outcome == acquire.OUTCOME_NETWORK
    assert result.attempts == 3
    assert waits == [1.0, 2.0]
    assert store.current_file("202401") is None


def test_missing_file_is_reported_not_retried(store: Store) -> None:
    calls = []
    dl, _ = downloader(store, lambda r: calls.append(1) or httpx.Response(404))
    assert dl.download_month("202101").outcome == acquire.OUTCOME_NOT_FOUND
    assert len(calls) == 1


def test_truncated_zip_is_rejected_and_kept_as_evidence(store: Store, zip_bytes: bytes) -> None:
    dl, _ = downloader(store, lambda r: httpx.Response(200, content=zip_bytes[:-40]))
    result = dl.download_month("202401")
    assert result.outcome == acquire.OUTCOME_INVALID
    assert not store.bronze_path("202401").exists()
    assert len(list(store.rejected.glob("202401_NFe.*.rejected"))) == 1
    state = {s.month: s for s in month_statuses(store)}["202401"]
    assert state.state == d.STATE_INVALID


def test_concurrent_download_of_several_months(store: Store, zip_bytes: bytes) -> None:
    dl, _ = downloader(store, lambda r: httpx.Response(200, content=zip_bytes))
    months = ["202401", "202402", "202403", "202404"]
    results = dl.download_many(months, concurrency=3)
    assert {r.outcome for r in results} == {acquire.OUTCOME_OK}
    assert all(store.current_file(m) for m in months)


def test_a_validated_file_settles_a_blocked_month(store: Store, zip_bytes: bytes) -> None:
    dl, _ = downloader(store, lambda r: httpx.Response(405, content=WAF_PAGE))
    dl.download_month("202401")
    assert store.month_row("202401")["blocked"] == 1
    dl2, _ = downloader(store, lambda r: httpx.Response(200, content=zip_bytes))
    assert dl2.download_month("202401").outcome == acquire.OUTCOME_OK
    assert store.month_row("202401")["blocked"] == 0


# -- manual import -----------------------------------------------------------------------------
def test_manual_import_applies_the_same_validation(store: Store, tmp_path: Path) -> None:
    source = tmp_path / "202401_NFe.zip"
    baseline_month(source)
    result = acquire.import_zip(store, source)
    assert result.accepted and result.month == "202401"
    row = store.current_file("202401")
    assert row["origem"] == "IMPORTACAO_MANUAL"
    assert row["sha256"] == result.sha256
    assert store.bronze_path("202401").read_bytes() == source.read_bytes()
    state = {s.month: s for s in month_statuses(store)}["202401"]
    assert state.state == d.STATE_VALIDATED  # a manual file settles the month even if unlisted


def test_manual_import_refuses_html_and_unknown_month(store: Store, tmp_path: Path) -> None:
    page = tmp_path / "202402_NFe.zip"
    page.write_bytes(WAF_PAGE)
    refused = acquire.import_zip(store, page)
    assert not refused.accepted and refused.detail == "pagina_html_no_lugar_do_zip"
    assert store.current_file("202402") is None
    assert store.month_row("202402")["invalid"] == 1

    nameless = tmp_path / "download.zip"
    baseline_month(nameless)
    assert not acquire.import_zip(store, nameless).accepted
    assert acquire.import_zip(store, nameless, month="202403").accepted


def test_manual_import_compares_with_the_reference_hash(store: Store, tmp_path: Path) -> None:
    source = tmp_path / "202401_NFe.zip"
    baseline_month(source)
    wrong = acquire.import_zip(store, source, reference_hashes={"202401": "0" * 64})
    assert wrong.reference_match is False
    right = acquire.import_zip(store, source, reference_hashes={"202401": wrong.sha256})
    assert right.reference_match is True
    assert store.current_file("202401")["reference_match"] == 1


def test_a_different_file_supersedes_but_keeps_history(store: Store, tmp_path: Path) -> None:
    first = tmp_path / "202401_NFe.zip"
    baseline_month(first)
    acquire.import_zip(store, first)
    second = tmp_path / "other" / "202401_NFe.zip"
    second.parent.mkdir()
    from tests.helpers.cgu_nfe_synthetic import build_zip, note_row

    build_zip(second, "202401", [note_row(9)], [])
    acquire.import_zip(store, second)
    assert store.current_file("202401")["sha256"] != ""
    statuses = [r["status"] for r in store.files() if r["month"] == "202401"]
    assert statuses == ["SUPERSEDED", "VALIDATED"]
