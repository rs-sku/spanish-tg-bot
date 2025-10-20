import json
import logging

from src.core.constansts import Constants
from src.services.db_service import DbService
from src.services.redis_service import RedisService
from src.utils.log_decorator import async_log_decorator
from src.utils.translator_client import TranslatorClient
from src.utils.word_validation import validate_word

logger = logging.getLogger(__name__)


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

    async def show_words(self, chat_id: int, is_repeat: bool, is_base: bool = False) -> str | None:
        words = await self._cache_words(chat_id, is_repeat, is_base)
        if not words:
            return
        res = ""
        for word_tr in words:
            res += f"{list(word_tr.keys())[0]} - {list(word_tr.values())[0]}\n"
        return res

    def get_random_word(self, chat_id: int) -> dict[str, str] | None:
        redis_res = self._redis_service.get_random_word(chat_id)
        if not redis_res:
            return
        return json.loads(redis_res)

    def get_all_cached_words(self, chat_id: int) -> list[str]:
        redis_words = self._redis_service.get_all_words(chat_id)
        return [list(json.loads(word_tr).keys())[0] for word_tr in redis_words]

    def move_word(self, chat_id: int, word_tr: dict[str, str]) -> None:
        self._redis_service.move_word(chat_id, json.dumps(word_tr))

    async def get_random_variants(self, chat_id: int) -> list[str]:
        return await self._db_service.get_random_variants(chat_id)

    async def translate_and_add_user_word(self, chat_id: int, rus_word: str) -> str | None:
        if not await validate_word(rus_word):
            raise ValueError()
        spanish_word = await self._translator.translate_one(rus_word, Constants.SPANISH_DEST.value)
        rus_word, spanish_word = rus_word.capitalize(), spanish_word.capitalize()
        if not await self._db_service.add_user_word(chat_id, spanish_word, rus_word):
            return
        return f'"{rus_word} - {spanish_word}"'

    async def add_user_word(self, chat_id: int, word: str) -> str | None:
        if not await self._db_service.add_user_word(chat_id, word):
            return
        return word

    async def add_user_words(self, chat_id: int) -> bool:
        redis_words = self._redis_service.get_all_words(chat_id)
        if not redis_words:
            return False
        words = [list(json.loads(word_tr).keys())[0] for word_tr in redis_words]
        await self._db_service.add_user_words(chat_id, words)
        return True

    async def delete_user_word(self, chat_id: int, rus_word: str) -> str | None:
        rus_word = rus_word.capitalize()
        if not await self._db_service.delete_user_word(chat_id, rus_word):
            return
        return f'"{rus_word}"'

    def validate_input_word(self, word: str) -> bool:
        return word.isalpha()

    async def check_has_repeat_words(self, chat_id: int) -> bool:
        return await self._db_service.get_repeat_words(chat_id) is not None

    @async_log_decorator(logger)
    async def get_page_of_words(self, chat_id: int, page: int) -> tuple[list[str] | bool] | None:
        count = await self._db_service.count_user_words(chat_id)
        if count == 0:
            return
        prev = page > 1
        next_ = count > Constants.USER_WORDS_PAGE_SIZE.value * page
        offset = (page - 1) * Constants.USER_WORDS_PAGE_SIZE.value
        words = await self._db_service.get_paginated_words(
            chat_id,
            Constants.USER_WORDS_PAGE_SIZE.value,
            offset,
        )
        if not words:
            return
        res = [f"{word_tr['word']} - {word_tr['translation']}" for word_tr in words]
        return res, prev, next_

    async def _cache_words(
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
        data = [json.dumps(word_tr) for word_tr in words]
        self._redis_service.add_words(chat_id, data)
        return words
