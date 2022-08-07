from typing import List, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    xlwings_api_key: Optional[str]
    google_allowed_domains: Optional[List]

    class Config:
        env_file = ".env"


settings = Settings()
