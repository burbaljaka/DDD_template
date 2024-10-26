from typing import Protocol, TypeVar, get_args, Optional, final, List

from sqlalchemy import select, inspect, Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.db import Base

# mapper_registry = registry(metadata=metadata)
# generate_base = mapper_registry.generate_base()

_MT = TypeVar("_MT", bound=Base)  # Model Type
_T = TypeVar("_T")  # Primary key Type


class BaseAsyncRepository(Protocol):
    _session: AsyncSession

    @property
    def session(self) -> AsyncSession:
        assert self._session is not None
        return self._session


class AsyncRepository(BaseAsyncRepository, Protocol[_MT, _T]):


    @property
    def _model(self):
        return get_args(self.__orig_bases__[0])[0]

    @property
    def _pk_column(self) -> str:
        return inspect(self._model).primary_key[0].name

    async def find_by_pk(self, pk: _T) -> Optional[_MT]:
        return await self.find_by_col(**{self._pk_column: pk})

    async def delete(self, item: _MT):
        await self.session.delete(item)

    # async def create(self, obj_in: dict):
    #     query = insert(self.model).values(**obj_in).returning(self.model.id)
    #     res = await self.session.execute(query)
    #     return res.scalars().one_or_none()

    @final
    def create(self, item: _MT):
        self.session.add(item)


    @final
    async def create_all(self, items: List[_MT]):
        self.session.add_all(items)

    @final
    async def find_all(self, **kwargs) -> List[_MT]:
        stmt = self._gen_stmt_for_param(**kwargs)
        result = await self.session.execute(stmt)

        return result.unique().scalars().fetchall()

    @final
    async def find_all_by_query(self, row_filter) -> List[_MT]:
        stmt = self._gen_stmt_for_query(row_filter=row_filter)
        result = await self.session.execute(stmt)
        return result.unique().scalars().fetchall()

    @staticmethod
    def update(item, req: dict):
        for k, v in req.items():
            if v is not None:
                setattr(item, k, v)

    @final
    async def find_by_col(self, **kwargs) -> Optional[_MT]:
        item = await self.session.execute(self._gen_stmt_for_param(**kwargs))
        return item.unique().scalars().one_or_none()

    @final
    def _gen_stmt_for_param(self, **kwargs) -> Select:
        stmt = select(self._model)
        if kwargs:
            for key, value in kwargs.items():
                stmt = stmt.where(getattr(self._model, key) == value)
        return stmt

    @final
    def _gen_stmt_for_query(self, row_filter) -> Select:
        return select(self._model).where(row_filter)

