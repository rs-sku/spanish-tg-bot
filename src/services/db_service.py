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
