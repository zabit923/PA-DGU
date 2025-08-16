from typing import Optional, Sequence

from fastapi import APIRouter


class BaseRouter:
    def __init__(self, prefix: str = "", tags: Optional[Sequence[str]] = None):
        self.router = APIRouter(prefix=f"/{prefix}" if prefix else "", tags=tags or [])
        self.configure()

    def configure(self):
        """Переопределяется в дочерних классах для настройки роутов"""

    def get_router(self) -> APIRouter:
        return self.router
