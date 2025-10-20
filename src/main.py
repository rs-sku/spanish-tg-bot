import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from googletrans import Translator
from redis import Redis

from src.bot.bot import LangBot
from src.bot.middlewares import ButtonInterceptionMsgMiddleware
from src.core.db import Database
from src.core.settings import Settings
from src.repositories import db_repo, redis_repo
from src.services import db_service, redis_service, seed_service
from src.services.coordinator import Coordinator
from src.utils import translator_client

logger = logging.getLogger(__name__)


async def on_startup(db: Database) -> db_repo.DbRepo:
    logging.basicConfig(level=logging.INFO)
    await db.init(
        user=Settings.POSTGRES_USER,
        password=Settings.POSTGRES_PASSWORD,
        database=Settings.POSTGRES_DB,
        host=Settings.POSTGRES_HOST,
        port=Settings.POSTGRES_PORT,
    )
    repo = db_repo.DbRepo(db.pool)
    seed = seed_service.SeedService(repo)
    await seed.init()
    return repo


async def on_shutdown(db: Database, bot: Bot) -> None:
    await db.close()
    await bot.session.close()
    logger.info("Shutdown complete")


async def main() -> None:
    db = None
    bot_obj = None
    try:
        db = Database()
        db_rep = await on_startup(db)
        db_serv = db_service.DbService(db_rep)
        redis = Redis(Settings.REDIS_HOST, Settings.REDIS_PORT, decode_responses=True)
        redis_rep = redis_repo.RedisRepo(redis)
        redis_serv = redis_service.RedisService(redis_rep)
        translator = Translator()
        tr_client = translator_client.TranslatorClient(translator)
        coordinator = Coordinator(redis_serv, db_serv, tr_client)
        bot_obj = Bot(Settings.BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())
        dp.message.middleware(ButtonInterceptionMsgMiddleware())
        bot = LangBot(dp, bot_obj, coordinator)
        await bot.start()
    finally:
        await on_shutdown(db, bot_obj)


if __name__ == "__main__":
    asyncio.run(main())
