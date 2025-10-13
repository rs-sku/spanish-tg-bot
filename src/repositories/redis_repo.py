import redis
import logging
from src.utils.log_decorator import sync_log_decorator
from src.core.constansts import Constants


logger = logging.getLogger(__name__)


class RedisRepo:
    def __init__(self, r: redis.Redis) -> None:
        self._r = r

    @sync_log_decorator(logger)
    def in_process(self, user_id: int) -> bool:
        return bool(self._r.get(f"user:{user_id}"))

    @sync_log_decorator(logger)
    def set_in_process(self, user_id: int) -> None:
        self._r.set(f"user:{user_id}", 1, ex=60)

    @sync_log_decorator(logger)
    def remove_in_process(self, user_id: int) -> None:
        self._r.delete(f"user:{user_id}")

    @sync_log_decorator(logger)
    def add_words(self, chat_id: int, words_to_add: list[str]) -> None:
        self._r.set(chat_id, Constants.ATTEMPTS_COUNT.value)
        self._r.sadd(f"{chat_id}:{Constants.ATTEMPTS_COUNT.value}", *words_to_add)

    @sync_log_decorator(logger)
    def get_random_word(self, chat_id: int) -> str | None:
        count = self._get_attempts_count(chat_id)
        if not count:
            return
        if count > 0:
            return self._r.srandmember(f"{chat_id}:{count}")

    @sync_log_decorator(logger)
    def move_word(self, chat_id: int, word: str) -> None:
        count = self._get_attempts_count(chat_id)
        new_count = count - 1
        new_key = f"{chat_id}:{new_count}"
        if new_count >= 0:
            self._r.smove(f"{chat_id}:{count}", f"{new_key}", word)
            if new_count == 0:
                self._r.expire(new_key, 3600)
                self._r.expire(chat_id, 3600)

    @sync_log_decorator(logger)
    def get_all_words(self, chat_id: int) -> set[str]:
        count = self._get_attempts_count(chat_id)
        return self._r.smembers(f"{chat_id}:{count}")

    @sync_log_decorator(logger)
    def delete_words(self, chat_id: int) -> None:
        keys = self._r.keys(f"{chat_id}:*")
        if keys:
            self._r.delete(*keys)

    def reduce_attempts_count(self, chat_id: int) -> int | None:
        count = self._get_attempts_count(chat_id)
        if not count:
            return
        new_count = count - 1
        if new_count < 0:
            return
        self._r.set(chat_id, new_count)
        return new_count

    def _get_attempts_count(self, chat_id) -> int | None:
        count = self._r.get(chat_id)
        return int(count) if count else None
