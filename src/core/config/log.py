from pydantic import Field

from src.core.config import BaseSettings


class LogSettings(BaseSettings):
    level: str = Field(default="INFO")
