import json
from src.core.constansts import Constants
from src.repositories.db_repo import DbRepo


class DbService:
    def __init__(self, repo: DbRepo) -> None:
        self._repo = repo

    async def get_repeat_words(self, chat_id: int) -> list[str]:
        words = await self._repo.get_repeat_words(chat_id)
        return [json.dumps(word_tr) for word_tr in words]

    async def save_user_words(self, chat_id: int, words: set[str]) -> None:
        words = [json.loads(word) for word in words]
        self._repo.save_user_words(chat_id, words)
