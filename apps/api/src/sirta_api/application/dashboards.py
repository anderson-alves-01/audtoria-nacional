from sqlalchemy.orm import Session

from sirta_api.application.official_ingest import list_official_gold
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import HOMOLOGATION_PENDING, OFFICIAL_BANNER
from sirta_api.domain.dashboards import DASHBOARDS, dashboard_by_id
from sirta_api.domain.errors import NotVisibleError


def list_dashboards(session: Session, *, context: AccessContext) -> dict:
    context.ensure_fiscal_read()
    gold = list_official_gold(session, context=context)
    return {
        "banner": OFFICIAL_BANNER,
        "homologationStatus": HOMOLOGATION_PENDING,
        "createsTaxCredit": False,
        "commandsDisabled": True,
        "items": [
            _view(item, gold_items=gold["items"])
            for item in DASHBOARDS
        ],
    }


def get_dashboard(session: Session, *, context: AccessContext, dashboard_id: str) -> dict:
    context.ensure_fiscal_read()
    catalog = dashboard_by_id(dashboard_id)
    if catalog is None:
        raise NotVisibleError()
    gold = list_official_gold(session, context=context)
    return _view(catalog, gold_items=gold["items"], empty_sources=gold["emptySources"])


def _view(
    catalog: dict, *, gold_items: list[dict], empty_sources: list[dict] | None = None
) -> dict:
    if catalog.get("includeAllGold"):
        items = list(gold_items)
    else:
        allowed = set(catalog.get("goldSourceIds") or ())
        items = [item for item in gold_items if item.get("sourceId") in allowed]
    return {
        "id": catalog["id"],
        "path": catalog["path"],
        "title": catalog["title"],
        "banner": OFFICIAL_BANNER,
        "homologationStatus": HOMOLOGATION_PENDING,
        "createsTaxCredit": False,
        "commandsDisabled": True,
        "emptyReason": catalog["emptyReason"],
        "published": bool(items),
        "items": items,
        "emptySources": empty_sources or [],
        "roiCalculated": False,
        "taxPotentialAsCredit": False,
    }
