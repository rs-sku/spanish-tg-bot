import redis
import logging
import json
from uuid import uuid4
from src.utils import log_decorator
from src.core.constansts import Constants


logger = logging.getLogger(__name__)



class RedisRepo:
    def __init__(self, r: redis.Redis) -> None:
        self._r = r

    @log_decorator(logger)
    def set_user_word(self, chat_id: int, word_tr: str, attempts_count: int) -> None:
        key = f"{chat_id}:{uuid4()}"
        value = json.dumps({"word_tr": word_tr, "attempts_count": attempts_count})
        self._r.set(key, value, ex=3600)

    @log_decorator(logger)
    def get_keys(self, chat_id: int) -> list[str]:
        attempts_count = self.get_current_attempts_count(chat_id)
        keys = self._r.keys(f"{chat_id}:*")
        res = [
            k
            for k in keys
            if int(json.loads(self._r.get(k))["attempts_count"]) == attempts_count
        ]
        return res

    @log_decorator(logger)
    def change_value(self, key: str, value: str) -> None:
        self._r.set(key, value)

    @log_decorator(logger)
    def get_user_word(self, key: str) -> str:
        word_tr = json.loads(self._r.get(key))["word_tr"]
        return word_tr

    @log_decorator(logger)
    def get_all_words(self, chat_id: int) -> list[str]:
        keys = self.get_keys(chat_id)[:Constants.SHOW_COUNT.value]
        res = [self.get_user_word(key) for key in keys]
        return res

    @log_decorator(logger)
    def delete_key(self, key: str) -> None:
        self._r.delete(key)

    @log_decorator(logger)
    def set_current_attempts_count(self, chat_id: int, attempts_count: int) -> None:
        self._r.set(chat_id, attempts_count)

    @log_decorator(logger)
    def get_current_attempts_count(self, chat_id) -> int:
        return int(self._r.get(chat_id))
