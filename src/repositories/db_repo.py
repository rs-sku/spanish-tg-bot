import asyncpg

from src.core.constansts import Constants


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

    async def add_user_word(self, chat_id: int, word: str, translate: str) -> None:
        async with self._pool.acquire() as conn:
            query = """
                    INSERT INTO users (chat_id)
                    VALUES ($1)
                    RETURNING id;
                    """
            user_id = await conn.fetchval(query, chat_id)
            query = """
                    INSERT INTO main_words (word, translation)
                    VALUES ($1, $2)
                    RETURNING id;
                    """
            word_id = await conn.fetchval(query, word, translate)

            await conn.execute(
                """
                INSERT INTO users_words (user_id, word_id)
                VALUES ($1, %2);
                """,
                (user_id, word_id),
            )

    async def delete_user_word(self, word: str, chat_id: int) -> None:
        word_id = await self._get_word_id(word)
        user_id = await self._get_user_id(chat_id)
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM users_words
                WHERE word_id=%1 and user_id=%2
                """,
                (word_id, user_id),
            )

    async def get_random_words(self, chat_id: int) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """                
                SELECT *
                FROM users_words
                WHERE chat_id=%1
                ORDER BY RANDOM()
                LIMIT %2;
                """,
                (chat_id, Constants.SHOW_COUNT.value),
            )

    async def _get_user_id(self, chat_id: int) -> int:
        async with self._pool.acquire() as conn:
            query = """
                    SELECT id FROM users
                    WHERE chat_id=%1;
                    """
            return await conn.fetchval(query, chat_id)

    async def _get_word_id(self, word: str) -> int:
        async with self._pool.acquire() as conn:
            query = """
                    SELECT id FROM words
                    WHERE word=%1;
                    """
            return await conn.fetchval(query, word)
