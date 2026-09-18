import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from sirta_api.adapters.db.models import Base
from sirta_api.adapters.db.seed import seed_synthetic
from sirta_api.adapters.db.session import get_session
from sirta_api.config import get_settings
from sirta_api.entrypoints.main import create_app


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
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
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
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    get_settings.cache_clear()
