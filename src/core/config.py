from pathlib import Path

from environs import Env
from pydantic import BaseModel
from pydantic_settings import BaseSettings

DEBUG = True

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "db.sqlite3"

env = Env()
env.read_env()

DB_USERNAME = env.str("POSTGRES_USER")
DB_PASSWORD = env.str("POSTGRES_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")
DB_DATABASE = env.str("POSTGRES_DB")

SECRET_KEY = env.str("SECRET_KEY")
RESET_PASSWORD_TOKEN_SECRET = env.str("RESET_PASSWORD_TOKEN_SECRET")
VERIFICATION_TOKEN_SECRET = env.str("VERIFICATION_TOKEN_SECRET")


class SecretKey(BaseModel):
    secret_key: str = SECRET_KEY
    reset_password_token_secret: str = RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret: str = VERIFICATION_TOKEN_SECRET


class DbSettings(BaseModel):
    url: str = (
        f"sqlite+aiosqlite:///{DB_PATH}"
        if DEBUG
        else f"postgresql+asyncpg://"
        f"{DB_USERNAME}:"
        f"{DB_PASSWORD}@"
        f"{DB_HOST}:"
        f"{DB_PORT}/"
        f"{DB_DATABASE}"
    )
    echo: bool = True


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    secret: SecretKey = SecretKey()


settings = Settings()
