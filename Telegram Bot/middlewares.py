from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from database import cache_user


class UsernameCacheMiddleware(BaseMiddleware):
    # запоминает всех кто пишет в чат (id + username)
    # нужно чтобы находить людей по @username и строить отчёт

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.from_user:
            cache_user(event.chat.id, event.from_user.id, event.from_user.username)

        return await handler(event, data)
