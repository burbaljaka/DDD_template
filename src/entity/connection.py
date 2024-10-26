from asyncio import current_task
from contextlib import asynccontextmanager
from typing import Callable, Optional

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_scoped_session, create_async_engine, \
    async_sessionmaker

from src.entity.db import Base


class AsyncSQLAlchemy:
    def __init__(self, db_uri: str) -> None:
        self._db_uri = db_uri
        self._engine: Optional[AsyncEngine] = None
        self._session_factory = None

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def connect(self, **kwargs):
        if not kwargs:
            self._engine = create_async_engine(
                self._db_uri,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=1800
            )
        else:
            self._engine = create_async_engine(self._db_uri, **kwargs)

    async def disconnect(self):
        await self._engine.dispose()

    def init_session_factory(self, autocommit: bool = False, autoflush: bool = False):
        self._session_factory = async_scoped_session(
            async_sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=self._engine, class_=AsyncSession),
            scopefunc=current_task)

    @asynccontextmanager
    async def session(self) -> Callable[..., AsyncSession]:
        assert self._session_factory is not None

        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def get_db_session(self) -> Callable[..., AsyncSession]:
        assert self._session_factory is not None

        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @property
    def engine(self):
        assert self._engine is not None
        return self._engine

    @property
    def session_factory(self):
        assert self._session_factory is not None
        return self._session_factory
