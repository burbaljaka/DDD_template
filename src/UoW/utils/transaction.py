from typing import Any, Callable

from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.base_service import BaseService


async def __async_requires_new(self, func, read_only: bool, session: AsyncSession, args, kwargs):
    if not session.is_active:
        await session.begin()

    result = await func(self, *args, **kwargs)
    if not read_only:
        await session.commit()
        try:
            inspect(result)
            await session.refresh(result)
        except NoInspectionAvailable:
            pass
    return result


def async_transactional(
    uc_for_reuse_session: list[str] | None = None, *, read_only: bool = False
):
    def decorator(func: Callable):
        async def wrapper(use_case: BaseService, *args, **kwargs):
            if not use_case.uow._session:  # for main use_case
                async with use_case.uow:
                    _set_session_in_use_cases(use_case, uc_for_reuse_session)
                    result = await func(use_case, *args, **kwargs)

                    if not read_only:
                        await _end_write_session(use_case, result)

                    return result

            else:  # for nested use_case
                async with use_case.uow(reuse_session=True):
                    _set_session_in_use_cases(use_case, uc_for_reuse_session)
                    return await func(use_case, *args, **kwargs)

        return wrapper

    return decorator


def _set_session_in_use_cases(
    use_case: BaseService, nested_use_cases: list[str] | None
):
    if nested_use_cases:
        for nested_uc_name in nested_use_cases:
            nested_use_case: BaseService = getattr(use_case, nested_uc_name)
            nested_use_case.uow._session = use_case.uow.session


async def _end_write_session(use_case: BaseService, result: Any):
    await use_case.uow.session.commit()
    try:
        inspect(result)
        await use_case.uow.session.refresh(result)
    except NoInspectionAvailable as e:
        print(e)
        pass
