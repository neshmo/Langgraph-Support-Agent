from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(..., env="OPENROUTER_MODEL")
    database_url: str = Field(..., env="DATABASE_URL")
    app_env: str = Field("development", env="APP_ENV")

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()
