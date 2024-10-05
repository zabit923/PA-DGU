from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from environs import Env

DEBUG = True

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "db.sqlite3"
env = Env()
env.read_env()


db_drivername = 'postgresql+asyncpg',
db_username = env.str('POSTGRES_USER'),
db_password = env.str('POSTGRES_PASSWORD'),
db_host = env.str('DB_HOST'),
db_port = env.int('DB_PORT'),
db_database = env.str('POSTGRES_DB'),


class DbSettings(BaseModel):
    url: str = (
        f"sqlite+aiosqlite:///{DB_PATH}" if DEBUG else
        f"postgresql+asyncpg://{db_username}:{db_password}@{db_host}:{db_port}/{db_database}"
    )
    echo: bool = True


class Settings(BaseSettings):
    db: DbSettings = DbSettings()


settings = Settings()
