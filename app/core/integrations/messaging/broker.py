from faststream import FastStream
from faststream.rabbit.fastapi import RabbitRouter

from app.core.settings import settings

rabbit_router = RabbitRouter(
    settings.rabbitmq_url,
    reconnect_interval=5.0,
)

broker = rabbit_router.broker
app = FastStream(broker)
