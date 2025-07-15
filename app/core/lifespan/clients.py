from typing import List

from fastapi import FastAPI

from app.core.connections import BaseClient
from app.core.lifespan.base import register_shutdown_handler, register_startup_handler


class ClientsManager(BaseClient):
    def __init__(self):
        super().__init__()
        self.clients: List[BaseClient] = []

    async def connect(self) -> None:
        from app.core.connections import RabbitMQClient, RedisClient

        self.clients = [RedisClient(), RabbitMQClient()]

        for client in self.clients:
            await client.connect()

        self.logger.info("Подключено клиентов: %s", len(self.clients))

    async def close(self) -> None:
        for client in self.clients:
            await client.close()

        self.logger.info("Закрыто клиентов: %s", len(self.clients))


clients_manager = ClientsManager()


@register_startup_handler
async def initialize_clients(app: FastAPI):
    app.state.clients_manager = clients_manager
    await clients_manager.connect()


@register_shutdown_handler
async def close_clients(app: FastAPI):
    await app.state.clients_manager.close()
