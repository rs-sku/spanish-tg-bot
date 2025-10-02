from src.repositories.db_repo import DbRepo


class DbService:
    def __init__(self, repo: DbRepo) -> None:
        self._repo = repo

    async def add_word(self, chat_id: int, word: str) -> None:
        pass
