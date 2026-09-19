import argparse
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from sirta_api.adapters.db.seed import seed_identity
from sirta_api.adapters.db.session import get_session_factory
from sirta_api.adapters.db.synthetic_ids import (
    PURPOSE_ALPHA_ACTIVE,
    TENANT_ALPHA,
    TERRITORY_ALPHA_CENTRO,
    USER_ADMIN_ALPHA,
)
from sirta_api.adapters.ingest.catalog_loader import catalog_sources
from sirta_api.application.source_ingest import ingest_catalog_source
from sirta_api.domain.authorization import AccessContext
from sirta_api.domain.catalog import ingest_allowed
from sirta_api.domain.identities import Role


def _admin_context() -> AccessContext:
    return AccessContext(
        user_id=USER_ADMIN_ALPHA,
        tenant_id=TENANT_ALPHA,
        territory_id=TERRITORY_ALPHA_CENTRO,
        purpose_id=PURPOSE_ALPHA_ACTIVE,
        role=Role.TECH_ADMIN,
        purpose_expires_at=None,
        username="admin.alpha",
    )


def run_official_ingest(session: Session, *, source_ids: list[str] | None = None) -> list[dict]:
    context = _admin_context()
    wanted = set(source_ids or [])
    results = []
    for item in catalog_sources():
        source_id = item["source_id"]
        if wanted and source_id not in wanted:
            continue
        if not ingest_allowed(
            source_role=item["source_role"],
            access_classification=item["access_classification"],
            status=item["status"],
            fixture_kind=item["fixture_kind"],
        ):
            results.append({"sourceId": source_id, "skipped": True, "status": item["status"]})
            continue
        try:
            body = ingest_catalog_source(session, context=context, source_id=source_id)
            session.commit()
            results.append(body)
        except Exception as exc:
            session.rollback()
            results.append(
                {
                    "sourceId": source_id,
                    "skipped": False,
                    "failed": True,
                    "error": str(exc),
                }
            )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest cataloged PUBLIC_OPEN official sources")
    parser.add_argument("--sources", default="", help="Comma-separated source IDs")
    args = parser.parse_args()
    source_ids = [item.strip() for item in args.sources.split(",") if item.strip()]
    session = get_session_factory()()
    try:
        seed_identity(session)
        session.flush()
        results = run_official_ingest(session, source_ids=source_ids or None)
        session.commit()
        extracted = datetime.now(UTC).isoformat()
        print({"extractedAtUtc": extracted, "results": results})
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
