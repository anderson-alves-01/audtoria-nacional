from sqlalchemy.orm import Session

from sirta_api.application.official_ingest import (
    list_dashboard_chart_lines,
    list_official_gold,
    list_statement_revenue_totals,
)
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import (
    HOMOLOGATION_REFERENCE_VALIDATED,
    OFFICIAL_BANNER,
)
from sirta_api.domain.dashboard_charts import (
    STATEMENT_REVENUE_SOURCES,
    build_dashboard_visuals,
    build_statement_revenue_charts,
    items_for_chart_lines,
    separate_measures,
    statement_revenue_account_codes,
)
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
    view["items"] = _newest_competence_first(view["items"])
    scoped_lines = list_dashboard_chart_lines(
        session, context=context, items=items_for_chart_lines(view["items"])
    )
    visuals = build_dashboard_visuals(items=view["items"], lines=scoped_lines)
    separate_measures(view["items"], scoped_lines)
    view["kpis"] = visuals["kpis"]
    view["charts"] = [
        *visuals["charts"],
        *build_statement_revenue_charts(
            list_statement_revenue_totals(
                session,
                context=context,
                source_ids=_statement_sources(view["items"]),
                accounts=statement_revenue_account_codes(),
            )
        ),
    ]
    return view


def _statement_sources(items: list[dict]) -> list[str]:
    present = {str(item.get("sourceId") or "") for item in items}
    return [source_id for source_id in STATEMENT_REVENUE_SOURCES if source_id in present]


def _newest_competence_first(items: list[dict]) -> list[dict]:
    """The reading surface takes the first row of a source as the figure's competence."""
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(str(item.get("sourceId") or ""), []).append(item)
    ordered: list[dict] = []
    for source in sorted(grouped):
        ordered.extend(
            sorted(
                grouped[source],
                key=lambda item: str(item.get("competence") or ""),
                reverse=True,
            )
        )
    return ordered


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
