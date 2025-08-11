# import logging
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool  # , inspect
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.settings import settings

# logger = logging.getLogger("alembic.autogenerate")
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section
# Для быстрых миграций без запуска бд, но сначала alembic upgrade head
# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
# config.set_section_option(section, "sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
config.set_section_option(section, "sqlalchemy.url", str(settings.database_dsn))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.models import BaseModel

target_metadata = BaseModel.metadata

# Выводим информацию о таблицах в метаданных
# logger.info("Таблицы в метаданных:")
# for table_name in target_metadata.tables.keys():
#     logger.info(f"  - {table_name}")

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    # Выводим информацию о таблицах в базе данных
    # inspector = inspect(connection)
    # db_tables = inspector.get_table_names()
    # logger.info("Таблицы в базе данных:")
    # for table_name in db_tables:
    #     logger.info(f"  - {table_name}")
    context.configure(
        connection=connection, target_metadata=target_metadata, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    connectable = config.attributes.get("connection", None)

    if connectable is None:
        asyncio.run(run_async_migrations())
    else:
        do_run_migrations(connectable)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
