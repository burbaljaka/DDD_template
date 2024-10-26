import sqlalchemy as sa

from src.tests.fake_data.fake_data import create_fake_users, create_fake_devices, insert_fake_users, \
    insert_fake_devices, insert_fake_roles, insert_fake_devices_to_roles, insert_fake_user_roles, create_fake_roles, \
    create_fake_device_roles, create_fake_user_roles

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
    await insert_fake_users(session, create_fake_users())
    await insert_fake_devices(session, create_fake_devices())
    await insert_fake_roles(session, create_fake_roles())
    await insert_fake_devices_to_roles(session, create_fake_device_roles())
    await insert_fake_user_roles(session, create_fake_user_roles())

    yield

    await session.execute(
        sa.text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE;")
    )
    await session.commit()


@pytest.fixture
def admin_user():
    return create_fake_users()[0]


@pytest.fixture
def common_user():
    return create_fake_users()[1]


@pytest.fixture
def common_user_device():
    return create_fake_devices()[1]


@pytest.fixture
def not_common_user_device():
    return create_fake_devices()[0]


@pytest.fixture
def get_devices():
    return create_fake_devices()
