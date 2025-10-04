from datetime import datetime, timezone
import asyncpg

from src.core.constansts import Constants
import logging

from src.utils.log_decorator import async_log_decorator

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
                chat_id BIGINT NOT NULL UNIQUE
                );                            
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS words(
                id SERIAL PRIMARY KEY,
                word VARCHAR(64) NOT NULL UNIQUE,
                translation VARCHAR(64) NOT NULL,
                is_base BOOLEAN NOT NULL
                );
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

    @async_log_decorator(logger)
    async def add_all_words(self, words: list[dict[str, str | bool]]) -> None:
        async with self._pool.acquire() as conn:
            if not words:
                return
            values_sql = ", ".join(
                f"(${i * 3 + 1}, ${i * 3 + 2}, ${i * 3 + 3})" for i in range(len(words))
            )
            query = f"""
                    INSERT INTO words (word, translation, is_base)
                    VALUES {values_sql}
                    ON CONFLICT (word) DO NOTHING
                    """
            params = []
            for w in words:
                params.extend([w["word"], w["translation"], w["is_base"]])
            await conn.execute(query, *params)

    async def count_words(self) -> int:
        async with self._pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM words")

    @async_log_decorator(logger)
    async def add_user_word(self, chat_id: int, word: str) -> None:
        user_id = await self._get_user_id(chat_id)
        if not user_id:
            user_id = await self._add_user(chat_id)

        async with self._pool.acquire() as conn:
            word_id = await self._get_word_id(word)
            await conn.execute(
                """
                INSERT INTO users_words (user_id, word_id)
                VALUES ($1, $2)
                """,
                user_id,
                word_id,
            )

    @async_log_decorator(logger)
    async def get_random_words(
        self, chat_id: int, is_base: bool, limit: int
    ) -> list[asyncpg.Record]:
        user_id = await self._get_user_id(chat_id)
        if not user_id:
            user_id = await self._add_user(chat_id)
        async with self._pool.acquire() as conn:
            query = """
                    SELECT w.id, w.word, w.translation
                    FROM words w
                    LEFT JOIN users_words uw 
                        ON w.id = uw.word_id AND uw.user_id = $1
                    WHERE uw.word_id IS NULL
                    AND w.is_base = $2
                    ORDER BY RANDOM()
                    LIMIT $3
                    """
            rows = await conn.fetch(
                query,
                user_id,
                is_base,
                limit,
            )
            return rows

    @async_log_decorator(logger)
    async def add_user_words(self, chat_id, words: list[str]) -> None:
        user_id = await self._get_user_id(chat_id)
        if not user_id:
            user_id = await self._add_user(chat_id)
        async with self._pool.acquire() as conn:
            words_ids = [await self._get_word_id(word) for word in words]
            await conn.executemany(
                "INSERT INTO users_words (user_id, word_id) VALUES ($1, $2)",
                [(user_id, w_id) for w_id in words_ids],
            )

    @async_log_decorator(logger)
    async def delete_user_word(self, word: str, chat_id: int) -> None:
        word_id = await self._get_word_id(word)
        user_id = await self._get_user_id(chat_id)
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM users_words
                WHERE word_id=$1 and user_id=$2
                """,
                word_id,
                user_id,
            )

    @async_log_decorator(logger)
    async def get_repeat_words(self, chat_id: int) -> list[asyncpg.Record] | None:
        async with self._pool.acquire() as conn:
            ids = await self._get_repeat_words_ids(chat_id)
            if not ids:
                return
            query = """
                    SELECT word, translation from words
                    WHERE id = ANY($1::int[])
                    """
            rows = await conn.fetch(query, ids)
            return rows

    async def _get_repeat_words_ids(self, chat_id: int) -> list[int] | None:
        user_id = await self._get_user_id(chat_id)
        if not user_id:
            user_id = await self._add_user(chat_id)
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                query = """                
                        SELECT word_id
                        FROM users_words
                        WHERE user_id=$1
                        ORDER BY last_seen ASC
                        LIMIT $2
                        FOR UPDATE
                        """
                rows = await conn.fetch(
                    query,
                    user_id,
                    Constants.SHOW_COUNT.value,
                )
                if not rows:
                    return
                ids = [row["word_id"] for row in rows]
                await conn.execute(
                    """
                    UPDATE users_words
                    SET last_seen = $1
                    WHERE user_id = $2 AND word_id = ANY($3::int[])
                    """,
                    datetime.now(timezone.utc),
                    user_id,
                    ids,
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
