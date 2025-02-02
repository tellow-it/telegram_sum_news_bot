import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    # db
    DB_PORT = os.getenv("DB_PORT")
    DB_HOST = os.getenv("DB_HOST")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")

    PG_DATABASE_URL = \
        (f"postgresql+asyncpg://"
         f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
         f"{DB_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    # redis
    REDIS_PORT = os.getenv("REDIS_PORT")
