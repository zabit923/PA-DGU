from pathlib import Path
from typing import Literal

from environs import Env
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# __________________________________________________________________________________________________


env = Env()
env.read_env()


DEBUG = env.bool("DEBUG")

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "sqlite3.db"


LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s"
)

DB_USERNAME = env.str("POSTGRES_USER")
DB_PASSWORD = env.str("POSTGRES_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.int("DB_PORT")
DB_DATABASE = env.str("POSTGRES_DB")

JWT_ALGORITHM = "HS256"

SECRET_KEY = env.str("SECRET_KEY")
RESET_PASSWORD_TOKEN_SECRET = env.str("RESET_PASSWORD_TOKEN_SECRET")
VERIFICATION_TOKEN_SECRET = env.str("VERIFICATION_TOKEN_SECRET")

EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")


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
    url: str = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    test_url: str = "sqlite+aiosqlite:///test.db"
    echo: bool = True


class RedisSettings(BaseModel):
    url: str = f"redis://{env.str('REDIS_HOST')}:{env.int('REDIS_PORT')}"


class EmailSettings(BaseModel):
    email_host_user: str = EMAIL_HOST_USER
    email_host_password: str = EMAIL_HOST_PASSWORD


static_dir = BASE_DIR / "static"
media_dir = static_dir / "media"

# __________________________________________________________________________________________________


class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    db: DbSettings = DbSettings()
    redis: RedisSettings = RedisSettings()
    secret: SecretKey = SecretKey()
    logging: LoggingConfig = LoggingConfig()
    email: EmailSettings = EmailSettings()


settings = Settings()
