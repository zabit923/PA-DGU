from .api import email_test_router

# Импортируем и инициализируем брокер
from .broker import broker, rabbit_router

# Импортируем публичные классы и функции для использования в других модулях
from .producers import EmailProducer, MessageProducer

__all__ = [
    "rabbit_router",
    "broker",
    "MessageProducer",
    "EmailProducer",
    "email_test_router",
]
