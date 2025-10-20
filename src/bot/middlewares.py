from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Update

from src.bot.constants import ButtonsText


class ButtonInterceptionMsgMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        state: FSMContext = data.get("state")
        if isinstance(event, Message):
            buttons_text = [b.value for b in ButtonsText]
            if event.text in buttons_text:
                if state:
                    await state.clear()
        return await handler(event, data)
