from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Resolve .env relative to this file so it works from any working directory
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)


class Settings(BaseSettings):
    OPENAI_API_KEY: str

    class Config:
        env_file = _env_path
        env_file_encoding = "utf-8"


settings = Settings()
