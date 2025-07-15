from fastapi import FastAPI

from app.core.dependencies import database_client
from app.core.lifespan.base import register_shutdown_handler, register_startup_handler


@register_startup_handler
async def initialize_database(app: FastAPI):
    await database_client.connect()
    app.state.database_client = database_client


@register_shutdown_handler
async def close_database_connection(app: FastAPI):
    if hasattr(app.state, "database_client"):
        await app.state.database_client.close()
