from src.core.constansts import Constants
from src.services.redis_service import RedisService
from src.services.db_service import DbService
from src.translator_client import TranslatorClient
import json


class Coordinator:
    def __init__(
        self,
        redis_service: RedisService,
        db_service: DbService,
        translator_client: TranslatorClient,
    ) -> None:
        self._redis_service = redis_service
        self._db_service = db_service
        self._translator = translator_client

    async def show_words(
        self, chat_id: int, is_repeat: bool, is_base: bool = False
    ) -> str | None:
        words = await self._add_words(chat_id, is_repeat, is_base)
        if not words:
            return
        res = ""
        for word_tr in words:
            res += f"{list(word_tr.keys())[0]} - {list(word_tr.values())[0]}\n"
        return res

    async def get_random_word_or_save(
        self, chat_id: int, saving: bool = False
    ) -> list[str] | None:
        redis_res = self._redis_service.get_random_word(chat_id)
        if isinstance(redis_res, str):
            return json.loads(redis_res)
        if saving:
            words = [list(json.loads(word_tr).keys())[0] for word_tr in redis_res]
            await self._db_service.save_user_words(chat_id, words)

    def move_word(self, chat_id: int, word_tr: dict[str, str]) -> None:
        self._redis_service.move_word(chat_id, json.dumps(word_tr))

    async def get_random_variants(self, chat_id: int) -> list[str]:
        return await self._db_service.get_random_variants(chat_id)

    async def _add_words(
        self,
        chat_id: int,
        is_repeat: bool,
        is_base: bool = False,
    ) -> list[dict[str, str]] | None:
        if is_repeat and not is_base:
            words = await self._db_service.get_repeat_words(chat_id)
            if not words:
                return
        else:
            words = await self._db_service.get_random_words(chat_id, is_base)
        if not words:
            return Constants.INTERNAL_ERROR.value
        data = [json.dumps(word_tr) for word_tr in words]
        await self._redis_service.add_words(chat_id, data)
        return words
