from sqlalchemy.orm import Session

from sirta_api.application.official_ingest import list_official_gold, list_official_gold_lines
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import (
    HOMOLOGATION_REFERENCE_VALIDATED,
    OFFICIAL_BANNER,
)
from sirta_api.domain.dashboard_charts import build_dashboard_visuals
from sirta_api.domain.dashboards import DASHBOARDS, dashboard_by_id
from sirta_api.domain.errors import NotVisibleError


def list_dashboards(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    gold = list_official_gold(session, context=context)
    return {
        "banner": OFFICIAL_BANNER,
        "homologationStatus": HOMOLOGATION_REFERENCE_VALIDATED,
        "createsTaxCredit": False,
        "commandsDisabled": True,
        "items": [_view(item, gold_items=gold["items"]) for item in DASHBOARDS],
    }


def get_dashboard(session: Session, *, context: AccessContext, dashboard_id: str) -> dict:
    context.ensure_fiscal_read()
    catalog = dashboard_by_id(dashboard_id)
    if catalog is None:
        raise NotVisibleError()
    gold = list_official_gold(session, context=context)
    view = _view(catalog, gold_items=gold["items"], empty_sources=gold["emptySources"])
    lines_payload = list_official_gold_lines(session, context=context)
    source_ids = {item.get("sourceId") for item in view["items"]}
    scoped_lines = [line for line in lines_payload["items"] if line.get("sourceId") in source_ids]
    visuals = build_dashboard_visuals(items=view["items"], lines=scoped_lines)
    view["kpis"] = visuals["kpis"]
    view["charts"] = visuals["charts"]
    return view


def _view(
    catalog: dict, *, gold_items: list[dict], empty_sources: list[dict] | None = None
) -> dict:
    all_empty = empty_sources or []
    if catalog.get("includeAllGold"):
        items = list(gold_items)
        scoped_empty = list(all_empty)
    else:
        allowed = set(catalog.get("goldSourceIds") or ())
        items = [item for item in gold_items if item.get("sourceId") in allowed]
        if allowed:
            scoped_empty = [item for item in all_empty if item.get("sourceId") in allowed]
        else:
            scoped_empty = []
    return {
        "id": catalog["id"],
        "path": catalog["path"],
        "title": catalog["title"],
        "banner": OFFICIAL_BANNER,
        "homologationStatus": HOMOLOGATION_REFERENCE_VALIDATED,
        "createsTaxCredit": False,
        "commandsDisabled": True,
        "emptyReason": catalog["emptyReason"],
        "published": bool(items),
        "items": items,
        "emptySources": scoped_empty,
        "roiCalculated": False,
        "taxPotentialAsCredit": False,
        "kpis": [],
        "charts": [],
    }
