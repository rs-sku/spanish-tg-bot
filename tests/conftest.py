import asyncpg
import pytest_asyncio
from src.repositories.db_repo import DbRepo
from src.repositories.redis_repo import RedisRepo
from src.services.redis_service import RedisService
from src.services.db_service import DbService
from src.services.coordinator import Coordinator
from src.core.settings import Settings

import pytest


@pytest.fixture
def redis_service(mocker):
    repo_mock = mocker.Mock()
    service = RedisService(repo_mock)
    return service, repo_mock


@pytest.fixture()
def db_service(mocker):
    repo = mocker.AsyncMock()
    service = DbService(repo)
    return service, repo


@pytest.fixture
def coordinator(mocker, redis_service, db_service):
    translator = mocker.AsyncMock()
    coordinator = Coordinator(redis_service[0], db_service[0], translator)
    return coordinator, translator


@pytest_asyncio.fixture()
async def db_pool():
    pool = await asyncpg.create_pool(
        (
            f"postgresql://{Settings.POSTGRES_USER}:"
            f"{Settings.POSTGRES_PASSWORD}@"
            f"{Settings.POSTGRES_HOST}:{Settings.POSTGRES_PORT}/"
            f"{Settings.POSTGRES_DB}"
        ),
        min_size=1,
        max_size=5,
    )
    yield pool
    await pool.close()


@pytest_asyncio.fixture()
async def db_repo(db_pool):
    repo = DbRepo(db_pool)
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await repo.create_tables()
    yield repo
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("TRUNCATE TABLE users_words, words, users CASCADE;")


@pytest.fixture
def redis_mock(mocker):
    r = mocker.Mock()
    return r


@pytest.fixture
def redis_repo(redis_mock):
    service = RedisRepo(redis_mock)
    return service, redis_mock
