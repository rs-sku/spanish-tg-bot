from src.core.constansts import Constants
from src.repositories.db_repo import DbRepo
from src.interfaces.i_db_service import DbServiceInterface


class DbService(DbServiceInterface):
    def __init__(self, repo: DbRepo) -> None:
        self._repo = repo

    async def get_repeat_words(self, chat_id: int) -> list[dict[str, str]] | None:
        rows = await self._repo.get_repeat_words(chat_id)
        if not rows:
            return
        return [{row["word"]: row["translation"]} for row in rows]

    async def save_user_words(self, chat_id: int, words: list[str]) -> None:
        await self._repo.add_user_words(chat_id, words)

    async def get_random_variants(self, chat_id: int) -> list[str]:
        rows = await self._repo.get_random_words(
            chat_id, True, Constants.VARIANTS_COUNT.value
        )
        return [row["word"] for row in rows]

    async def get_random_words(
        self, chat_id: int, is_base: bool
    ) -> list[dict[str, str]]:
        rows = await self._repo.get_random_words(
            chat_id, is_base, Constants.SHOW_COUNT.value
        )
        return [{row["word"]: row["translation"]} for row in rows]

    async def add_user_word(self, chat_id: int, word: str, translation: str) -> bool:
        return await self._repo.add_user_word(chat_id, word, translation)

    async def delete_user_word(self, chat_id: int, translation: str) -> bool:
        rows = await self._repo.get_by_translation(chat_id, translation)
        if not rows:
            return False
        for row in rows:
            if not await self._repo.delete_user_word(chat_id, row["word"]):
                return False
        return True
