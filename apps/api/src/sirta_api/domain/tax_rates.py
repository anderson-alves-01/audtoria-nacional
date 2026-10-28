"""Rate lookup by validity date. Pure functions, no I/O.

Rules, all fail closed:
- REVOGADO versions are never used.
- A VALIDADO version beats a PENDENTE one. If only PENDENTE versions apply, the result keeps
  status PENDENTE and the caller must label it as not legally validated.
- A date outside every window, an unknown UF or a tax without rate returns no rate.
- A year whose validated rate changes inside the year has no single annual rate: the result
  is ``changed_within_year`` and the rate is None. Annual data cannot be split.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

FLAT_TAXES = frozenset({"ITCD", "ITBI", "ISS"})
FLAT_UF = "BR"
USABLE_KINDS = frozenset({"MODAL", "UNICA"})


@dataclass(frozen=True)
class RateVersion:
    tax: str
    uf: str
    rate_kind: str
    rate: Decimal
    valid_from: date | None
    valid_to: date | None
    status: str
    legal_basis: str | None = None
    official_url: str | None = None


@dataclass(frozen=True)
class RateResolution:
    rate: Decimal | None
    status: str | None  # VALIDADO, PENDENTE or None when there is no rate
    version: RateVersion | None = None
    changed_within_year: bool = False


NO_RATE = RateResolution(rate=None, status=None)


def homologation_gaps(
    *,
    status: str,
    legal_basis: str | None,
    official_url: str | None,
    validated_by: str | None,
    valid_from: date | None,
) -> list[str]:
    """What is still missing before a rate version counts as homologated. Empty means complete.

    VALIDADO only says a legal basis was informed by a person. Homologation also needs the official
    URL of the legislation, a known start of validity and the person who validated it. A percentage
    read from an image, with none of these, is never homologated.
    """
    gaps: list[str] = []
    if status != "VALIDADO":
        gaps.append(
            "status diferente de VALIDADO" if status == "REVOGADO" else "validação jurídica"
        )
    if not (legal_basis or "").strip():
        gaps.append("fundamento legal")
    if not (official_url or "").strip():
        gaps.append("URL oficial da legislação")
    if not (validated_by or "").strip():
        gaps.append("responsável pela validação")
    if valid_from is None:
        gaps.append("início da vigência")
    return gaps


def is_homologated(**fields) -> bool:
    return not homologation_gaps(**fields)


def _matches(version: RateVersion, tax: str, uf: str | None) -> bool:
    if version.status == "REVOGADO" or version.tax != tax or version.rate_kind not in USABLE_KINDS:
        return False
    wanted = FLAT_UF if tax in FLAT_TAXES else uf
    return wanted is not None and version.uf == wanted


def _covers(version: RateVersion, start: date, end: date) -> bool:
    """True when the version window overlaps [start, end]. A NULL bound is open."""
    if version.valid_from is not None and version.valid_from > end:
        return False
    return not (version.valid_to is not None and version.valid_to < start)


def _preferred(candidates: list[RateVersion]) -> list[RateVersion]:
    validated = [v for v in candidates if v.status == "VALIDADO"]
    return validated or candidates


def resolve_on(versions: list[RateVersion], tax: str, uf: str | None, on: date) -> RateResolution:
    found = _preferred([v for v in versions if _matches(v, tax, uf) and _covers(v, on, on)])
    if not found:
        return NO_RATE
    # Latest start wins; an unknown start (NULL) loses to a known one.
    best = max(found, key=lambda v: v.valid_from or date.min)
    return RateResolution(rate=best.rate, status=best.status, version=best)


def resolve_year(
    versions: list[RateVersion], tax: str, uf: str | None, year: int
) -> RateResolution:
    start, end = date(year, 1, 1), date(year, 12, 31)
    found = _preferred([v for v in versions if _matches(v, tax, uf) and _covers(v, start, end)])
    if not found:
        return NO_RATE
    if len({v.rate for v in found}) > 1:
        return RateResolution(rate=None, status=found[0].status, changed_within_year=True)
    best = max(found, key=lambda v: v.valid_from or date.min)
    return RateResolution(rate=best.rate, status=best.status, version=best)
