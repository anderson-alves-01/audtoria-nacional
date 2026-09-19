from functools import lru_cache

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from sirta_api import IMPLEMENTATION_VERSION, RELEASE_STAGE, SPEC_VERSION

_LOCAL_DB_DEFAULT = "postgresql+psycopg://sirta:sirta_local_only@localhost:55432/sirta"
_LOCAL_S3_SECRET = "sirta_local_only"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "local"
    spec_version: str = SPEC_VERSION
    implementation_version: str = IMPLEMENTATION_VERSION
    release_stage: str = RELEASE_STAGE
    database_url: str = _LOCAL_DB_DEFAULT
    redis_url: str = "redis://localhost:6379/0"
    oidc_issuer: str = "http://localhost:8081/realms/sirta"
    oidc_audience: str = "sirta-api"
    oidc_jwks_url: str | None = "http://localhost:8081/realms/sirta/protocol/openid-connect/certs"
    oidc_jwks_path: str | None = None
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "sirta"
    s3_secret_key: str = _LOCAL_S3_SECRET
    s3_bucket: str = "sirta-local"
    allow_synthetic_loads: bool = Field(
        default=False,
        validation_alias=AliasChoices("SIRTA_ALLOW_SYNTHETIC_LOADS", "ALLOW_SYNTHETIC_LOADS"),
    )
    datalake_root: str = Field(
        default="var/datalake",
        validation_alias=AliasChoices("SIRTA_DATALAKE_ROOT", "DATALAKE_ROOT"),
    )
    official_http_timeout_seconds: float = 120.0

    @model_validator(mode="after")
    def reject_embedded_local_secrets_outside_local(self) -> "Settings":
        if self.environment.strip().lower() in {"", "local"}:
            return self
        if self.database_url == _LOCAL_DB_DEFAULT or "sirta_local_only" in self.database_url:
            raise ValueError(
                "Non-local environments require DATABASE_URL from the environment; "
                "embedded local credentials are forbidden"
            )
        if self.s3_secret_key == _LOCAL_S3_SECRET:
            raise ValueError(
                "Non-local environments require S3_SECRET_KEY from the environment; "
                "embedded local credentials are forbidden"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
