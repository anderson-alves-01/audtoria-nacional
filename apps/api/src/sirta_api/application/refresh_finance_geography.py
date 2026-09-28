"""Rebuild the Gold state summary from published municipal lines."""

from sqlalchemy import text

from sirta_api.adapters.db.session import get_session_factory
from sirta_api.application.finance_geography import refresh_published_finance_summaries


def main() -> None:
    session = get_session_factory()()
    try:
        session.execute(text("SET statement_timeout = 0"))
        count = refresh_published_finance_summaries(session)
        session.commit()
        print(f"FINANCE_STATE_SUMMARY rows={count}")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
