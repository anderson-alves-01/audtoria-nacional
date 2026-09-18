from pydantic_settings import BaseSettings, SettingsConfigDict

from sirta_api import IMPLEMENTATION_VERSION, RELEASE_STAGE, SPEC_VERSION


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"
    spec_version: str = SPEC_VERSION
    implementation_version: str = IMPLEMENTATION_VERSION
    release_stage: str = RELEASE_STAGE
    database_url: str = "postgresql+psycopg://sirta:sirta_local_only@localhost:5432/sirta"
    redis_url: str = "redis://localhost:6379/0"


def get_settings() -> Settings:
    return Settings()
