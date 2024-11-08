import logging

import uvicorn
from fastapi import FastAPI

from api.routers import router as api_router
from src.config import settings

logging.basicConfig(
    # level=logging.INFO
    format=settings.logging.log_format,
)


app = FastAPI()
app.include_router(
    api_router,
)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
