import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api import router as api_router
from core.config import settings

logging.basicConfig(
    # level=logging.INFO
    format=settings.logging.log_format,
)


app = FastAPI(
    default_response_class=ORJSONResponse,
)
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
