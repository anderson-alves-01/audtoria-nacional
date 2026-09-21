import os
from pathlib import Path

from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session
from tests.helpers.alembic_harness import drop_domain_tables, isolated_engine, upgrade_to

from sirta_api.adapters.db.models import Tenant, User
from sirta_api.adapters.db.seed import seed_synthetic
from sirta_api.adapters.db.synthetic_ids import TENANT_ALPHA, USER_COLLECTOR_ALPHA


def _app_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://sirta:sirta_local_only@localhost:55432/sirta",
    )


def test_upgrade_base_to_head_on_empty_database() -> None:
    with isolated_engine(_app_url()) as (engine, url):
        upgrade_to(url, "head")
        with engine.connect() as connection:
            version = connection.execute(text("SELECT version_num FROM alembic_version")).scalar()
            impl = connection.execute(
                text("SELECT value FROM schema_meta WHERE key = 'implementation_version'")
            ).scalar()
        assert version == "0051_ibge_sidra_cemp"
        assert impl == "0.3.48"
        with Session(engine) as session:
            seed_synthetic(session)
            session.commit()
            assert session.get(User, USER_COLLECTOR_ALPHA) is not None


def test_upgrade_0004_to_head_with_valid_seed() -> None:
    with isolated_engine(_app_url()) as (engine, url):
        upgrade_to(url, "0004_s2_validation")
        with Session(engine) as session:
            seed_synthetic(session)
            session.commit()
            assert session.get(Tenant, TENANT_ALPHA) is not None
        upgrade_to(url, "head")
        with Session(engine) as session:
            assert session.get(User, USER_COLLECTOR_ALPHA) is not None


def test_upgrade_0004_to_head_after_domain_drop_all() -> None:
    with isolated_engine(_app_url()) as (engine, url):
        upgrade_to(url, "0004_s2_validation")
        drop_domain_tables(engine)
        insp = inspect(engine)
        assert insp.has_table("tenants") is False
        assert insp.has_table("alembic_version") is True
        upgrade_to(url, "head")
        with Session(engine) as session:
            seed_synthetic(session)
            session.commit()
            assert session.get(Tenant, TENANT_ALPHA) is not None
            assert session.get(User, USER_COLLECTOR_ALPHA) is not None


def test_seed_synthetic_is_idempotent() -> None:
    with isolated_engine(_app_url()) as (engine, url):
        upgrade_to(url, "head")
        with Session(engine) as session:
            seed_synthetic(session)
            seed_synthetic(session)
            session.commit()
            tenants = session.scalar(select(func.count()).select_from(Tenant))
            collectors = session.scalar(
                select(func.count()).select_from(User).where(User.username == "collector.alpha")
            )
        assert tenants == 2
        assert collectors == 1


def test_collection_migration_does_not_seed_users() -> None:
    source = Path("alembic/versions/0005_s3_collection.py").read_text(encoding="utf-8")
    assert "collector.alpha" not in source
    assert "seed_synthetic" not in source
