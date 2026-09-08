from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"
    MAX_TOOL_ITERATIONS: int = 5
    CORS_ORIGINS: str = "http://localhost:3000"
    GUARD_API_URL: str = "http://localhost:8001"
    GUARD_TIMEOUT_SECONDS: float = 10.0

    @property
    def ai_configured(self) -> bool:
        return bool(self.OPENAI_API_KEY.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        if "*" in origins:
            raise ValueError("Wildcard CORS origins are not allowed")
        return origins


settings = Settings()
