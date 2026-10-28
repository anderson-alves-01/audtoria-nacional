"""Download with resume and manual import of the monthly ZIPs.

The host sits behind a human-verification wall for scripted GETs. When it answers with that wall
the month is recorded as blocked and a circuit breaker stops further attempts. The wall is never
bypassed: the official ZIP can be downloaded in a browser and brought in with ``import-zip``.
"""

from __future__ import annotations

import os
import re
import shutil
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import httpx

from sirta_api.adapters.ingest.cgu_nfe.store import Store
from sirta_api.adapters.ingest.cgu_nfe.zipcheck import (
    ZipReport,
    looks_like_html,
    sha256_file,
    validate_zip,
)
from sirta_api.domain.cgu_nfe import (
    bronze_name,
    is_month,
    month_from_filename,
    month_url,
)

OUTCOME_OK = "BAIXADO_VALIDADO"
OUTCOME_ALREADY = "JA_VALIDADO"
OUTCOME_BLOCKED = "DOWNLOAD_BLOQUEADO"
OUTCOME_INVALID = "ARQUIVO_INVALIDO"
OUTCOME_NOT_FOUND = "NAO_ENCONTRADO"
OUTCOME_NETWORK = "FALHA_DE_REDE"
OUTCOME_SKIPPED = "NAO_TENTADO"

CHUNK = 1024 * 256
RETRY_STATUS = {408, 425, 429, 500, 502, 503, 504}
WALL_STATUS = {401, 403, 405, 406, 429}


@dataclass
class DownloadResult:
    month: str
    outcome: str
    url: str
    http_status: int | None = None
    detail: str = ""
    sha256: str = ""
    size: int = 0
    attempts: int = 0


class CircuitBreaker:
    """Opens after ``limit`` consecutive human-verification answers. Thread-safe."""

    def __init__(self, limit: int = 3) -> None:
        self.limit = limit
        self._count = 0
        self._lock = threading.Lock()

    def record_block(self) -> None:
        with self._lock:
            self._count += 1

    def record_ok(self) -> None:
        with self._lock:
            self._count = 0

    @property
    def is_open(self) -> bool:
        with self._lock:
            return self._count >= self.limit


def _is_wall(status: int, body_prefix: bytes) -> bool:
    if body_prefix.startswith(b"PK"):
        return False
    return status == 405 or (status in WALL_STATUS and looks_like_html(body_prefix))


def _ref_hash(reference: dict[str, str] | None, month: str) -> str | None:
    return None if not reference else reference.get(month)


class Downloader:
    def __init__(
        self,
        store: Store,
        client: httpx.Client,
        *,
        retries: int = 3,
        backoff: float = 2.0,
        max_wait: float = 60.0,
        breaker_limit: int = 3,
        pause: float = 0.0,
        sleep: Callable[[float], None] = time.sleep,
        reference_hashes: dict[str, str] | None = None,
    ) -> None:
        self.store = store
        self.client = client
        self.retries = max(1, retries)
        self.backoff = backoff
        self.max_wait = max_wait
        self.breaker = CircuitBreaker(breaker_limit)
        self.pause = pause
        self.sleep = sleep
        self.reference_hashes = reference_hashes
        self._db_lock = threading.Lock()

    # -- one month --------------------------------------------------------------------------
    def download_month(self, month: str, *, force: bool = False) -> DownloadResult:
        url = month_url(month)
        result = DownloadResult(month, OUTCOME_SKIPPED, url)
        with self._db_lock:
            self.store.upsert_month(month, url=url)
            current = self.store.current_file(month)
        target = self.store.bronze_path(month)
        if not force and current and target.is_file() and target.stat().st_size == current["size"]:
            result.outcome = OUTCOME_ALREADY
            result.sha256 = current["sha256"]
            result.size = current["size"]
            return result
        if self.breaker.is_open:
            result.detail = "disjuntor aberto: bloqueio de verificação humana repetido"
            return result

        part = self.store.partial / f"{month}_NFe.zip.part"
        for attempt in range(1, self.retries + 1):
            result.attempts = attempt
            outcome = self._attempt(month, url, part, result)
            if outcome != "RETRY":
                break
            if attempt < self.retries:
                self.sleep(min(self.max_wait, self.backoff * 2 ** (attempt - 1)))
        else:
            result.outcome = OUTCOME_NETWORK
        if result.outcome == OUTCOME_NETWORK and not result.detail:
            result.detail = "tentativas esgotadas"
        self._record(month, result)
        if result.outcome == OUTCOME_OK and self.pause > 0:
            self.sleep(self.pause)  # courtesy pause between files, on our side
        return result

    def _attempt(self, month: str, url: str, part: Path, result: DownloadResult) -> str:
        start = part.stat().st_size if part.is_file() else 0
        headers = {"Range": f"bytes={start}-"} if start else {}
        try:
            with self.client.stream("GET", url, headers=headers) as response:
                status = response.status_code
                result.http_status = status
                if status == 416:
                    part.unlink(missing_ok=True)
                    result.detail = "HTTP 416: parcial descartado"
                    return "RETRY"
                if status in RETRY_STATUS and status != 429:
                    result.detail = f"HTTP {status}"
                    return "RETRY"
                if status not in (200, 206):
                    first = next(response.iter_bytes(CHUNK), b"")
                    return self._classify_refusal(result, status, first)
                if status == 206:
                    if not self._range_matches(response, start):
                        part.unlink(missing_ok=True)
                        result.detail = "resposta parcial incoerente; reiniciando"
                        return "RETRY"
                    mode = "ab"
                else:
                    mode = "wb"
                    start = 0
                expected = self._expected_total(response, start)
                first_chunk = True
                with part.open(mode) as handle:
                    for chunk in response.iter_bytes(CHUNK):
                        if first_chunk and start == 0:
                            first_chunk = False
                            if looks_like_html(chunk):
                                handle.close()
                                part.unlink(missing_ok=True)
                                return self._classify_refusal(result, status, chunk)
                        handle.write(chunk)
        except (httpx.TransportError, httpx.TimeoutException) as error:
            result.detail = f"{type(error).__name__}"
            return "RETRY"
        report = validate_zip(part, expected_size=expected)
        return self._finish_download(month, url, part, report, result)

    @staticmethod
    def _range_matches(response: httpx.Response, start: int) -> bool:
        match = re.match(r"bytes (\d+)-", response.headers.get("content-range", ""))
        return bool(match and int(match.group(1)) == start)

    @staticmethod
    def _expected_total(response: httpx.Response, start: int) -> int | None:
        crange = re.match(r"bytes \d+-\d+/(\d+)", response.headers.get("content-range", ""))
        if crange:
            return int(crange.group(1))
        length = response.headers.get("content-length")
        if length and length.isdigit() and not response.headers.get("content-encoding"):
            return start + int(length)
        return None

    def _classify_refusal(self, result: DownloadResult, status: int, body: bytes) -> str:
        if status == 404:
            result.outcome = OUTCOME_NOT_FOUND
            result.detail = "HTTP 404"
        elif _is_wall(status, body):
            result.outcome = OUTCOME_BLOCKED
            result.detail = f"HTTP {status} com página de verificação humana (WAF); não contornado"
            self.breaker.record_block()
        elif status == 429:
            result.outcome = OUTCOME_BLOCKED
            result.detail = "HTTP 429 limite de requisicoes"
            self.breaker.record_block()
        elif status == 200 and looks_like_html(body):
            result.outcome = OUTCOME_BLOCKED
            result.detail = "HTTP 200 com HTML no lugar do ZIP; não contornado"
            self.breaker.record_block()
        else:
            result.outcome = OUTCOME_NETWORK
            result.detail = f"HTTP {status} inesperado"
        return "FINAL"

    def _finish_download(
        self, month: str, url: str, part: Path, report: ZipReport, result: DownloadResult
    ) -> str:
        if not report.ok:
            rejected = self.store.rejected / f"{month}_NFe.{int(time.time())}.rejected"
            if part.is_file():
                shutil.move(str(part), rejected)
            result.outcome = OUTCOME_INVALID
            result.detail = report.reason
            result.size = report.size
            return "FINAL"
        os.replace(part, self.store.bronze_path(month))
        with self._db_lock:
            self.store.register_file(
                month=month,
                sha256=report.sha256,
                size=report.size,
                origem="DOWNLOAD",
                url_used=url,
                original_path=None,
                members=[m.__dict__ for m in report.members],
                reference_sha256=_ref_hash(self.reference_hashes, month),
            )
        result.outcome = OUTCOME_OK
        result.sha256 = report.sha256
        result.size = report.size
        self.breaker.record_ok()
        return "FINAL"

    def _record(self, month: str, result: DownloadResult) -> None:
        with self._db_lock:
            if result.outcome == OUTCOME_BLOCKED:
                self.store.set_blocked(month, result.detail)
            elif result.outcome == OUTCOME_INVALID:
                self.store.set_invalid(month, result.detail)
            elif result.outcome == OUTCOME_OK:
                self.store.set_blocked(month, None)
                self.store.set_invalid(month, None)

    # -- many -------------------------------------------------------------------------------
    def download_many(
        self, months: list[str], *, concurrency: int = 2, force: bool = False
    ) -> list[DownloadResult]:
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
            return list(pool.map(lambda m: self.download_month(m, force=force), months))


# -- manual import -----------------------------------------------------------------------------
@dataclass
class ImportResult:
    month: str
    accepted: bool
    detail: str
    sha256: str = ""
    size: int = 0
    reference_match: bool | None = None


def import_zip(
    store: Store,
    path: Path,
    *,
    month: str | None = None,
    reference_hashes: dict[str, str] | None = None,
) -> ImportResult:
    """Bring an official ZIP downloaded by hand into bronze, with the same checks as a download.

    The month comes from ``--month`` or from a file name like ``202401_NFe.zip``. A ZIP whose data
    does not belong to that month is refused later, by the processor, before anything is stored.
    """
    path = Path(path)
    month = month or month_from_filename(path.name)
    if not month or not is_month(month):
        return ImportResult("", False, "mês não identificado: informe --month AAAAMM")
    report = validate_zip(path)
    if not report.ok:
        store.upsert_month(month, url=month_url(month))
        store.set_invalid(month, f"importação manual recusada: {report.reason}")
        return ImportResult(month, False, report.reason, report.sha256, report.size)
    target = store.bronze_path(month)
    store.upsert_month(month, url=month_url(month))
    if not target.is_file() or sha256_file(target) != report.sha256:
        tmp = store.partial / f"{month}_NFe.zip.import"
        shutil.copyfile(path, tmp)
        os.replace(tmp, target)
    ref = _ref_hash(reference_hashes, month)
    store.register_file(
        month=month,
        sha256=report.sha256,
        size=report.size,
        origem="IMPORTACAO_MANUAL",
        url_used=None,
        original_path=str(path),
        members=[m.__dict__ for m in report.members],
        reference_sha256=ref,
    )
    store.set_invalid(month, None)
    store.set_blocked(month, None)
    match = None if ref is None else ref == report.sha256
    return ImportResult(month, True, bronze_name(month), report.sha256, report.size, match)
