from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    POSTGRES_DB: str = "demoshop"
    POSTGRES_USER: str = "demoshop"
    POSTGRES_PASSWORD: str = ""


settings = Settings()
