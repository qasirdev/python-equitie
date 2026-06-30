from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    openai_api_key: str = "dummy_key"  # for local scaffolding
    log_level: str = "info"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost"]

    class Config:
        env_file = ".env"


settings = Settings()
