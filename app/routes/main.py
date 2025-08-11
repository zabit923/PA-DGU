from fastapi.responses import RedirectResponse

from app.routes.base import BaseRouter


class MainRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="", tags=["Главная"])

    def configure(self):
        @self.router.get("/")
        async def root() -> RedirectResponse:
            return RedirectResponse(url="/docs")
