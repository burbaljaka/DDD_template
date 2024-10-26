import os

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton

from src.core.config import ApplicationSettings, settings
from src.entity.connection import AsyncSQLAlchemy


class BaseContainer(DeclarativeContainer):
    config = Configuration()
    config.from_dict(
        dict(
            ApplicationSettings(
                _env_file=os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                          + "/.env"
            )
        )
    )

    db = Singleton(AsyncSQLAlchemy, db_uri=settings.db.asyncpg_uri)