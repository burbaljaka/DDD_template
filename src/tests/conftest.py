import sqlalchemy as sa

# db_url = "postgresql+asyncpg://test_user:test_password@127.0.0.1:5435/test_db"
# engine = create_async_engine(db_url)

base_api_url = "/api"

import asyncio
import os
import time

import pytest
from dependency_injector.providers import Singleton
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.connection import AsyncSQLAlchemy
from src.app import app
from src.core.fastapi.mapper import start_mapper
from src.tests.utils import (
    get_container_status,
    get_db_uri,
    set_test_env,
    run_db_container,
)

# pytest_plugins = [
#     "tests.data.data_fixtures",
# ]


@pytest.fixture(scope="session")
def database():
    if os.getenv("APP_ENV") != 'local':
        yield

    else:
        set_test_env()
        container = run_db_container()
        container_status = "starting"
        while container_status not in {"healthy", "unhealthy"}:
            time.sleep(1)
            container_status = get_container_status(container.name)

        if container_status == "unhealthy":
            container.stop()
            pytest.exit("Test DB container not started")

        yield

        container.stop()


@pytest.fixture(scope="session")
async def migrations(database):
    pass
    # alembic_conf = Config("alembic.ini")
    # command.upgrade(alembic_conf, "head")


@pytest.fixture(scope="session", autouse=True)
async def db_override(migrations):
    app.container.db.override(Singleton(AsyncSQLAlchemy, get_db_uri()))
    db = app.container.db()
    await db.connect(poolclass=NullPool)
    await db.create_database()
    db.init_session_factory()
    start_mapper()

    yield db


@pytest.fixture
async def session(db_override) -> AsyncSession:
    async with db_override.session() as session:
        yield session


@pytest.fixture(scope="session")
async def async_client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale() -> list[str]:
    return ["ru_RU"]


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def table_names(db_override):
    async with db_override.engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: sa.inspect(sync_conn).get_table_names()
        )
        yield ",".join(tables)


@pytest.fixture
async def test_data(
        session,
        table_names
):
    ...
