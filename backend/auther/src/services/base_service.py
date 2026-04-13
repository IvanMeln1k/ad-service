from abc import ABC
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Callable, TypeVar, Coroutine

T = TypeVar("T")


class BaseService(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _execute_in_transaction(
        self, operation: Callable[[], Coroutine[Any, Any, T]]
    ) -> T:
        async with self.session.begin():
            try:
                result = await operation()
                return result
            except Exception:
                await self.session.rollback()
                raise
