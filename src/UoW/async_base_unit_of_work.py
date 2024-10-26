from abc import ABC, abstractmethod
from typing import Optional, Type


class AsyncBaseUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError("required __aenter__ call for UoW Pattern")

    async def __aexit__(
        self,
        exc_type: Optional[Type[Exception]],
        exc_val: Optional[Exception],
        traceback,
    ):
        if exc_type:
            await self.rollback()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError("Choice ORM commit func")

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError("Choice ORM rollback func")
