import redis
import logging
import json
from uuid import uuid4
from src.utils.log_decorator import log_decorator
from src.core.constansts import Constants


logger = logging.getLogger(__name__)


class RedisRepo:
    def __init__(self, r: redis.Redis) -> None:
        self._r = r

    @log_decorator(logger)
    def in_process(self, user_id: int) -> bool:
        return bool(self._r.get(f"user:{user_id}"))

    @log_decorator(logger)
    def set_in_process(self, user_id: int) -> None:
        self._r.set(f"user:{user_id}", 1, ex=60)

    @log_decorator(logger)
    def remove_in_process(self, user_id: int) -> None:
        self._r.delete(f"user:{user_id}")

    @log_decorator(logger)
    def add_words(self, chat_id: int, words_to_add: list[str]) -> None:
        self._r.set(chat_id, Constants.ATTEMPTS_COUNT.value)
        self._r.sadd(f"{chat_id}:{Constants.ATTEMPTS_COUNT.value}", *words_to_add)

    @log_decorator(logger)
    def get_random_word(self, chat_id: int) -> str | None:
        count = self._get_attempts_count(chat_id)
        if count > 0:
            return self._r.srandmember(f"{chat_id}:{count}")

    @log_decorator(logger)
    def move_word(self, chat_id: int, word: str) -> None:
        count = self._get_attempts_count(chat_id)
        new_count = count - 1
        if new_count >= 0:
            self._r.smove(f"{chat_id}:{count}", f"{chat_id}:{new_count}", word)

    @log_decorator(logger)
    def get_all(self, chat_id: int) -> set[str]:
        count = self._get_attempts_count(chat_id)
        return self._r.smembers(f"{chat_id}:{count}")

    @log_decorator(logger)
    def delete_words(self, chat_id: int) -> None:
        keys = self._r.keys(f"{chat_id}:*")
        if keys:
            logger.info(f"{keys=}")
            self._r.delete(*keys)

    def reduce_attempts_count(self, chat_id: int) -> int:
        count = self._get_attempts_count(chat_id)
        new_count = count - 1
        if new_count < 0:
            return
        self._r.set(chat_id, new_count)
        return new_count

    def _get_attempts_count(self, chat_id) -> int:
        return int(self._r.get(chat_id))
