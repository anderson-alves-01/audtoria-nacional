"""Inventory of the 60 months: what the catalog lists, what the host answers, what we hold."""

from __future__ import annotations

import re
from dataclasses import dataclass

import httpx

from sirta_api.adapters.ingest.cgu_nfe.store import Store
from sirta_api.adapters.ingest.http_client import USER_AGENT, official_ssl_context
from sirta_api.domain.cgu_nfe import (
    CATALOG_URL,
    PROCESSING_VERSION,
    derive_state,
    month_url,
    requested_months,
)

_PUSH = re.compile(
    r"arquivos\.push\(\s*\{\s*\"ano\"\s*:\s*\"(?P<ano>\d{4})\"\s*,\s*\"mes\"\s*:\s*\"(?P<mes>\d{1,2})\""
    r"[^}]*\"origem\"\s*:\s*\"(?P<origem>[^\"]*)\"",
)


def make_client(*, timeout: float = 120.0) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
        verify=official_ssl_context(),
        follow_redirects=True,
        timeout=httpx.Timeout(timeout, connect=30.0),
    )


def parse_catalog(html: str) -> set[str]:
    """Months (``AAAAMM``) that the catalog page lists for the NF-e origin."""
    found: set[str] = set()
    for match in _PUSH.finditer(html):
        if match["origem"].strip().lower() != "nfe":
            continue
        found.add(f"{match['ano']}{int(match['mes']):02d}")
    return found


class CatalogUnavailable(RuntimeError):
    pass


def fetch_catalog(client: httpx.Client, url: str = CATALOG_URL) -> set[str]:
    """Read the catalog page. A page that does not carry the list is an error, not 'no months'."""
    response = client.get(url)
    if response.status_code != 200:
        raise CatalogUnavailable(f"catálogo respondeu HTTP {response.status_code}")
    months = parse_catalog(response.text)
    if not months:
        raise CatalogUnavailable("catálogo sem a lista de arquivos (página alterada ou bloqueada)")
    return months


def probe_head(client: httpx.Client, month: str) -> tuple[int | None, int | None]:
    """Existence and size only. A HEAD answer is never evidence that a GET will be allowed."""
    try:
        response = client.head(month_url(month))
    except httpx.HTTPError:
        return None, None
    length = response.headers.get("content-length")
    size = int(length) if length and length.isdigit() else None
    return response.status_code, size


def refresh_inventory(
    store: Store, client: httpx.Client, *, probe: bool, months: list[str] | None = None
) -> dict[str, bool]:
    """Re-evaluate the listing (and optionally HEAD) for each month and store the facts."""
    months = months or requested_months()
    listed = fetch_catalog(client)
    result: dict[str, bool] = {}
    for month in months:
        is_listed = month in listed
        store.upsert_month(month, url=month_url(month), listed=is_listed)
        result[month] = is_listed
        if probe:
            status, size = probe_head(client, month)
            store.set_head(month, status, size)
    return result


@dataclass(frozen=True)
class MonthStatus:
    month: str
    state: str
    listed: bool
    url: str
    head_status: int | None
    head_size: int | None
    detail: str
    sha256: str
    processed: bool


def month_statuses(store: Store, months: list[str] | None = None) -> list[MonthStatus]:
    months = months or requested_months()
    out: list[MonthStatus] = []
    for month in months:
        row = store.month_row(month)
        file = store.current_file(month)
        done = bool(file and store.completed_processing(month, file["sha256"], PROCESSING_VERSION))
        # Never assume a month is listed: a month with no recorded check stays "not listed" until
        # the catalog was read.
        listed = bool(row and row["listed"])
        blocked = bool(row and row["blocked"])
        invalid = bool(row and row["invalid"])
        state = derive_state(
            listed=listed,
            blocked=blocked,
            invalid=invalid,
            validated=file is not None,
            processed=done,
        )
        detail = ""
        if row and row["blocked"]:
            detail = row["blocked_detail"] or ""
        elif row and row["invalid"]:
            detail = row["invalid_detail"] or ""
        out.append(
            MonthStatus(
                month=month,
                state=state,
                listed=listed,
                url=row["url"] if row else month_url(month),
                head_status=row["head_status"] if row else None,
                head_size=row["head_size"] if row else None,
                detail=detail,
                sha256=file["sha256"] if file else "",
                processed=done,
            )
        )
    return out
