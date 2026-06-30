from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    openai_api_key: str = "dummy_key"  # for local scaffolding
    log_level: str = "info"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
