import json
from venv import logger
from src.repositories.redis_repo import RedisRepo
from src.core.constansts import Constants
from src.translator_client import TranslatorClient
import random


class RedisService:
    def __init__(self, repo: RedisRepo, translator_client: TranslatorClient):
        self.words_to_show = []
        self._repo = repo
        self._translator_client = translator_client

    async def set_user_words(self, chat_id: int, words: list[str]) -> None:
        if self.words_to_show:
            return
        # self.words_to_show.append(None)  # Пока костыль чтобы не переполнять редис
        self._repo.set_current_attempts_count(chat_id, Constants.ATTEMPTS_COUNT.value)
        for word in words:
            translation = await self._translator_client.translate_one(word)
            word_tr = json.dumps({word: translation})
            self._repo.set_user_word(chat_id, word_tr, Constants.ATTEMPTS_COUNT.value)
        self.words_to_show = self._repo.get_all_words(chat_id)
        logger.info(f"{self.words_to_show=}")

    def show_all_words(self) -> str:
        res = ""
        for word_tr in self.words_to_show:
            word_tr = json.loads(word_tr)
            res += f"{list(word_tr.keys())[0]} - {list(word_tr.values())[0]}\n"
        return res

    def show_word(self, chat_id) -> tuple[dict[str, str] | str]:
        keys = self._repo.get_keys(chat_id)
        current_attempts_count = self._repo.get_current_attempts_count(chat_id)
        if not keys:
            current_attempts_count = current_attempts_count - 1
            if current_attempts_count <= 0:
                self.words_to_show = []  # Поменять когда будут добавляться в постгрес
                return
            self._repo.set_current_attempts_count(chat_id, current_attempts_count)
            keys = self._repo.get_keys(chat_id)
        key = random.choice(keys)
        word_tr = json.loads(self._repo.get_user_word(key))
        return word_tr, key

    def reduce_word_attempts_count(
        self, chat_id: int, word_tr: dict[str, str], key: str
    ) -> None:
        new_count = self._repo.get_current_attempts_count(chat_id) - 1
        if new_count <= 0:
            self._repo.delete_key(key)
        else:
            value = json.dumps(
                {"word_tr": json.dumps(word_tr), "attempts_count": new_count}
            )
            self._repo.change_value(key, value)
