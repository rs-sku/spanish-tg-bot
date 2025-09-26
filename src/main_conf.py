import os
from dotenv import load_dotenv

load_dotenv()


class MainConf:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    POSTGRES_DATABASE = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
