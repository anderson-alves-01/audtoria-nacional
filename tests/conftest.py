import os
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from tests.helpers.official_http import snapshot_http_client

from sirta_api.adapters.db.seed import seed_synthetic
from sirta_api.adapters.db.session import get_session
from sirta_api.adapters.ingest.deps import get_official_http_client
from sirta_api.config import get_settings
from sirta_api.entrypoints.main import create_app


def _alembic_upgrade(database_url: str) -> None:
    previous = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = database_url
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    try:
        command.upgrade(config, "head")
    finally:
        if previous is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous


@pytest.fixture(autouse=True)
def enable_synthetic_for_automated_tests(monkeypatch, tmp_path_factory) -> None:
    monkeypatch.setenv("SIRTA_ALLOW_SYNTHETIC_LOADS", "true")
    monkeypatch.setenv("SIRTA_DATALAKE_ROOT", str(tmp_path_factory.mktemp("datalake")))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://sirta:sirta_local_only@localhost:55432/sirta",
    )


@pytest.fixture(scope="session")
def engine(database_url: str):
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        pytest.fail(
            "PostgreSQL is required for F0 integration tests. "
            "Start it with: docker compose up -d postgres. "
            f"Original error: {exc}"
        )
    _alembic_upgrade(database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, expire_on_commit=False)()
    seed_synthetic(session)
    session.flush()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def api_client(db_session: Session, monkeypatch) -> Generator[TestClient, None, None]:
    monkeypatch.setenv("OIDC_JWKS_PATH", str(Path("tests/fixtures/jwt/jwks.json")))
    monkeypatch.setenv("OIDC_ISSUER", "http://localhost:8081/realms/sirta")
    monkeypatch.setenv("OIDC_AUDIENCE", "sirta-api")
    get_settings.cache_clear()

    def override_session():
        yield db_session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_official_http_client] = snapshot_http_client
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    get_settings.cache_clear()
