from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    google_allowed_domains: List

    class Config:
        env_file = ".env"


settings = Settings()
