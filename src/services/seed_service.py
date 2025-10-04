from src.core.constansts import Constants
from src.repositories.db_repo import DbRepo
import logging

logger = logging.getLogger(__name__)


class SeedService:
    def __init__(self, repo: DbRepo) -> None:
        self._repo = repo

    async def init(self) -> None:
        await self._repo.create_tables()
        await self._add_words()

    async def _add_words(self) -> None:
        with open(Constants.BASE_WORDS_FILE_PATH.value, "r", encoding="utf-8") as f:
            base_words = f.readlines()
        with open(Constants.WORDS_FILE_PATH.value, "r", encoding="utf-8") as f:
            words = f.readlines()
        words_table_size = await self._repo.count_words()
        if words_table_size and (words_table_size > Constants.MIN_WORDS_TABLE_SIZE.value):
            logger.info("Data already exists")
            return
        res = []
        for w in base_words:
            word_tr = w.split(":")
            res.append(
                {
                    "word": word_tr[0].strip().capitalize(),
                    "translation": word_tr[1].strip().capitalize(),
                    "is_base": True,
                }
            )
        for w in words:
            word_tr = w.split(":")
            res.append(
                {
                    "word": word_tr[0].strip().capitalize(),
                    "translation": word_tr[1].strip().capitalize(),
                    "is_base": False,
                }
            )
        await self._repo.add_all_words(res)
        logger.info("Db initialized")
