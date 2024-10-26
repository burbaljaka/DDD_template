from pydantic import Field, PositiveInt

from src.core.config import BaseSettings


class ServerSettings(BaseSettings):
    host: str = Field(default="127.0.0.1", alias="SERVER_HOST")
    port: PositiveInt = Field(default=8020, alias="SERVER_PORT")
    debug: bool = Field(default=True, alias="SERVER_DEBUG")
    reload: bool = Field(default=True, alias="SERVER_RELOAD")
