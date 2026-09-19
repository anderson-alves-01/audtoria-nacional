from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from sirta_api.adapters.db.models import Base

MIGTEST_NAME = "sirta_migtest"


def admin_url(database_url: str) -> str:
    return database_url.rsplit("/", 1)[0] + "/postgres"


def migtest_url(database_url: str) -> str:
    return database_url.rsplit("/", 1)[0] + f"/{MIGTEST_NAME}"


def ensure_migtest_database(database_url: str) -> str:
    target = migtest_url(database_url)
    engine = create_engine(admin_url(database_url), isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": MIGTEST_NAME},
            ).scalar()
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{MIGTEST_NAME}"'))
    finally:
        engine.dispose()
    return target


def reset_public_schema(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO CURRENT_USER"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO public"))


def alembic_config(url: str) -> Config:
    os.environ["DATABASE_URL"] = url
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    return config


def upgrade_to(url: str, revision: str) -> None:
    command.upgrade(alembic_config(url), revision)


def drop_domain_tables(engine: Engine) -> None:
    Base.metadata.drop_all(engine)


@contextmanager
def isolated_engine(database_url: str) -> Iterator[tuple[Engine, str]]:
    previous = os.environ.get("DATABASE_URL")
    url = ensure_migtest_database(database_url)
    engine = create_engine(url, pool_pre_ping=True)
    try:
        reset_public_schema(engine)
        yield engine, url
    finally:
        engine.dispose()
        if previous is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous
