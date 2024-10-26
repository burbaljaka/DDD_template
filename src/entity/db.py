import uuid

from decouple import config
from sqlalchemy import Integer, extract, MetaData
from sqlalchemy import UUID as SA_UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy.orm import registry
from sqlalchemy.sql.functions import now


def build_db_url():
    return f"postgresql+asyncpg://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"


def build_sync_db_url():
    return f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"


DB_CONFIG = {
    'host': config('DB_HOST'),
    'user': config('DB_USER'),
    'password': config('DB_PASSWORD'),
    'port': config('DB_PORT'),
    'database': config('DB_NAME')
}

_engine = create_async_engine(build_db_url(), pool_recycle=20)

_Session = async_sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
Base = mapper_registry.generate_base()


@declarative_mixin
class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(SA_UUID, primary_key=True, nullable=False, default=uuid.uuid4)


@declarative_mixin
class CreatedAtMixin:
    created_at: Mapped[int] = mapped_column(Integer, nullable=False, server_default=extract("EPOCH", now()))


def init_session() -> AsyncSession:
    return _Session()
