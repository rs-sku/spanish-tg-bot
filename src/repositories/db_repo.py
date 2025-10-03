from datetime import datetime
import asyncpg

from src.core.constansts import Constants
import logging
from src.utils.log_decorator import log_decorator

logger = logging.getLogger(__name__)


class DbRepo:
    def __init__(self, pool: asyncpg.pool.Pool) -> None:
        self._pool = pool

    async def create_tables(self) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL);                            
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS words(
                id SERIAL PRIMARY KEY,
                word VARCHAR(64) NOT NULL,
                translation VARCHAR(64) NOT NULL);
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users_words(
                user_id INT NOT NULL,
                word_id INT NOT NULL,
                last_seen TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),                               
                PRIMARY KEY (user_id, word_id), 
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE)
                """
            )

    @log_decorator(logger)
    async def add_user_word(self, chat_id: int, word: str, translate: str) -> None:
        async with self._pool.acquire() as conn:
            user_id = await self._get_user_id(chat_id)
            if not user_id:
                user_id = self._add_user(chat_id)
            query = """
                    INSERT INTO main_words (word, translation)
                    VALUES ($1, $2)
                    RETURNING id
                    """
            word_id = await conn.fetchval(query, word, translate)

            await conn.execute(
                """
                INSERT INTO users_words (user_id, word_id)
                VALUES ($1, $2)
                """,
                (user_id, word_id),
            )

    @log_decorator(logger)
    async def save_user_words(self, chat_id, words: list[dict[str, str]]) -> None:
        async with self._pool.acquire() as conn:
            user_id = self._get_user_id(chat_id)
            if not user_id:
                user_id = self._add_user(chat_id)
            values_sql = ", ".join(
                f"(${i * 2 + 1}, ${i * 2 + 2})" for i in range(len(words))
            )
            query = f"""
                    INSERT INTO main_words (word, translation)
                    VALUES {values_sql}
                    RETURNING id
                    """
            params = []
            for w in words:
                params.extend([w["word"], w["translation"]])
            rows = await conn.fetch(query, *params)
            words_ids = [row["id"] for row in rows]
            await conn.executemany(
                "INSERT INTO users_words (user_id, word_id) VALUES ($1, $2)",
                [(user_id, w_id) for w_id in words_ids],
            )

    @log_decorator(logger)
    async def delete_user_word(self, word: str, chat_id: int) -> None:
        word_id = await self._get_word_id(word)
        user_id = await self._get_user_id(chat_id)
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM users_words
                WHERE word_id=$1 and user_id=$2
                """,
                (word_id, user_id),
            )

    @log_decorator(logger)
    async def get_repeat_words(self, chat_id: int) -> list[dict[str, str]]:
        async with self._pool.acquire() as conn:
            ids = await self._get_repeat_words_ids(chat_id)
            rows = conn.fetch(
                """
                SELECT word, translation from words
                WHERE id = ANY($1::int[0])
                """,
                (ids,),
            )
            return {row["word"]: row["translation"] for row in rows}

    @log_decorator(logger)
    async def _get_repeat_words_ids(self, chat_id: int) -> list[int]:
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                rows = await conn.fetch(
                    """                
                    SELECT id, word_id
                    FROM users_words
                    WHERE chat_id=$1
                    ORDER BY last_seen ASC
                    LIMIT $2
                    FOR UPDATE
                    """,
                    (chat_id, Constants.SHOW_COUNT.value),
                )
                if not rows:
                    return
                ids = [row["id"] for row in rows]
                await conn.execute(
                    """
                    UPDATE users_words
                    SET last_seen = $1
                    WHERE id = ANY($2::int[])
                    """,
                    (
                        datetime.now(datetime.timezone.utc),
                        ids,
                    ),
                )

                return [row["word_id"] for row in rows]

    async def _get_user_id(self, chat_id: int) -> int | None:
        async with self._pool.acquire() as conn:
            query = """
                    SELECT id FROM users
                    WHERE chat_id=$1
                    """
            return await conn.fetchval(query, chat_id)

    async def _get_word_id(self, word: str) -> int:
        async with self._pool.acquire() as conn:
            query = """
                    SELECT id FROM words
                    WHERE word=$1
                    """
            return await conn.fetchval(query, word)

    async def _add_user(self, chat_id: int) -> int:
        async with self._pool.acquire() as conn:
            query = """
                    INSERT INTO users (chat_id)
                    VALUES ($1)
                    RETURNING id
                    """
            return await conn.fetchval(query, chat_id)
