from pydantic import Field, PostgresDsn

from src.core.config import BaseSettings


class DatabaseSettings(BaseSettings):
    database_uri: PostgresDsn | str = "postgresql://dev:dev@localhost:5436/dev"
    # database_uri: PostgresDsn | str = "postgresql://dev:dev@localhost:5436/dev"

    @property
    def asyncpg_uri(self):
        s = str(self.database_uri)
        if "asyncpg" not in s:
            return s.replace("postgresql", "postgresql+asyncpg")

        return s
