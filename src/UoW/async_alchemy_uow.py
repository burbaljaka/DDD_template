from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.UoW.async_base_unit_of_work import AsyncBaseUnitOfWork


class AsyncAlchemyUnitOfWork(AsyncBaseUnitOfWork):
    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._session: Optional[AsyncSession] = None
        self._reuse_session: bool = False

    def __call__(self, *, reuse_session: bool = False):
        self._reuse_session = reuse_session
        return self

    @property
    def engine(self) -> AsyncEngine:
        assert self._engine is not None
        return self._engine

    @property
    def session(self) -> AsyncSession:
        assert self._session is not None
        return self._session

    async def __aenter__(self):
        if not self._session or not self._reuse_session:
            self._session = AsyncSession(self.engine)

    async def __aexit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_val: Optional[Exception],
        traceback,
    ):
        if not self._reuse_session:
            await super().__aexit__(exc_type, exc_val, traceback)

            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def flush(self):
        await self.session.flush()

    async def refresh(self, item):
        await self.session.refresh(item)

    async def rollback(self):
        await self.session.rollback()

    def add(self, item):
        self.session.add(item)
