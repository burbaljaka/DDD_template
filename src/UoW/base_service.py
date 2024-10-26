from typing import Protocol, TypeVar, Union

from src.UoW.async_base_unit_of_work import AsyncBaseUnitOfWork

_UT = TypeVar("_UT", bound=Union[AsyncBaseUnitOfWork])


class BaseUseCase(Protocol[_UT]):
    _uow: _UT

    @property
    def uow(self) -> _UT:
        assert self._uow is not None
        return self._uow
