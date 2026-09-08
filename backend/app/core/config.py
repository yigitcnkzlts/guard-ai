from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    DEMOSHOP_BASE_URL: str
    UPSTREAM_TIMEOUT_SECONDS: float = 5.0
    CORS_ORIGINS: str = "http://localhost:3000"
    GATEWAY_API_KEY: str | None = None
    GATEWAY_RATE_LIMIT: int = 120
    MAX_REQUEST_BODY_BYTES: int = 262144
    ADMIN_API_KEY: str | None = None
    TENANT_ENFORCEMENT: bool = False
    REDIS_URL: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        if "*" in origins:
            raise ValueError("Wildcard CORS origins are not allowed")
        return origins


settings = Settings()
