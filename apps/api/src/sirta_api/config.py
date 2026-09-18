from functools import lru_cache

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
    oidc_issuer: str = "http://localhost:8081/realms/sirta"
    oidc_audience: str = "sirta-api"
    oidc_jwks_url: str | None = "http://localhost:8081/realms/sirta/protocol/openid-connect/certs"
    oidc_jwks_path: str | None = None
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "sirta"
    s3_secret_key: str = "sirta_local_only"
    s3_bucket: str = "sirta-local"


@lru_cache
def get_settings() -> Settings:
    return Settings()
