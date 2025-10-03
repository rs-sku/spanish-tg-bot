import json
import time
from src.repositories.redis_repo import RedisRepo
from src.core.constansts import Constants
from src.translator_client import TranslatorClient
import random
import logging
from src.utils.log_decorator import log_decorator

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self, repo: RedisRepo, translator_client: TranslatorClient):
        self._repo = repo
        self._translator_client = translator_client

    async def add_user_words(self, chat_id: int, words: list[str]) -> None:
        if self._repo.in_process(chat_id):
            return
        self._repo.set_in_process(chat_id)
        self._repo.delete_words(chat_id)
        words_to_set = []
        for word in words:
            translation = await self._translator_client.translate_one(word)
            word_tr = json.dumps({word: translation})
            words_to_set.append(word_tr)
        self._repo.add_words(chat_id, words_to_set)

    @log_decorator(logger)
    def show_all_words(self, chat_id: int) -> str:
        words = self._repo.get_all(chat_id)
        res = ""
        for word_tr in words:
            word_tr = json.loads(word_tr)
            res += f"{list(word_tr.keys())[0]} - {list(word_tr.values())[0]}\n"
        self._repo.remove_in_process(chat_id)
        return res

    def get_random_word(self, chat_id: int) -> dict[str, str]:
        word = self._repo.get_random_word(chat_id)
        if not word:
            count = self._repo.reduce_attempts_count(chat_id)
            if count == 0:
                res = self._repo.get_all(chat_id)
                self._repo.delete_words(chat_id)
                return  # возвращать res потом
            word = self._repo.get_random_word(chat_id)
        return json.loads(word)

    def move_word(self, chat_id: int, word_tr: dict[str, str]) -> None:
        self._repo.move_word(chat_id, json.dumps(word_tr))
