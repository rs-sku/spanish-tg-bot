from src.repositories.redis_repo import RedisRepo
from src.interfaces.i_redis_service import RedisServiceInterface
import logging
from src.utils.log_decorator import sync_log_decorator

logger = logging.getLogger(__name__)


class RedisService(RedisServiceInterface):
    def __init__(self, repo: RedisRepo) -> None:
        self._repo = repo

    @sync_log_decorator(logger)
    def add_words(self, chat_id: int, words: list[str]) -> None:
        if self._repo.in_process(chat_id):
            return
        self._repo.set_in_process(chat_id)
        self._repo.delete_words(chat_id)
        self._repo.add_words(chat_id, words)
        self._repo.remove_in_process(chat_id)

    def get_random_word(self, chat_id: int) -> str | None:
        word = self._repo.get_random_word(chat_id)
        if not word:
            count = self._repo.reduce_attempts_count(chat_id)
            if not count or count == 0:
                return
            word = self._repo.get_random_word(chat_id)
        return word

    def get_all_words(self, chat_id: int) -> set[str]:
        return self._repo.get_all_words(chat_id)

    def move_word(self, chat_id: int, word_tr: str) -> None:
        self._repo.move_word(chat_id, word_tr)
