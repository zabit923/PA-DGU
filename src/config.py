from pathlib import Path
from typing import Literal

from environs import Env
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# __________________________________________________________________________________________________


DEBUG = True

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "sqlite3.db"

env = Env()
env.read_env()

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

DB_USERNAME = env.str("POSTGRES_USER")
DB_PASSWORD = env.str("POSTGRES_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")
DB_DATABASE = env.str("POSTGRES_DB")

SECRET_KEY = env.str("SECRET_KEY")
RESET_PASSWORD_TOKEN_SECRET = env.str("RESET_PASSWORD_TOKEN_SECRET")
VERIFICATION_TOKEN_SECRET = env.str("VERIFICATION_TOKEN_SECRET")


# __________________________________________________________________________________________________


class SecretKey(BaseModel):
    secret_key: str = SECRET_KEY
    reset_password_token_secret: str = RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret: str = VERIFICATION_TOKEN_SECRET


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT


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


# __________________________________________________________________________________________________


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    db: DbSettings = DbSettings()
    secret: SecretKey = SecretKey()
    logging: LoggingConfig = LoggingConfig()


settings = Settings()
