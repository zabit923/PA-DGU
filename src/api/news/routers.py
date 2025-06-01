from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from starlette import status

from api.users.dependencies import get_current_user
from core.database.models import User
from core.utils.paginated_response import PaginatedResponse

from .schemas import NewsCreate, NewsRead, NewsUpdate
from .service import NewsService, news_service_factory

router = APIRouter(prefix="/news")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NewsRead)
async def add_news(
    title: str = Form(...),
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    news_service: NewsService = Depends(news_service_factory),
    user: User = Depends(get_current_user),
):
    news_data = NewsCreate(title=title, text=text)
    new_news = await news_service.create_news(user, news_data, image)
    return new_news


@router.patch("/{news_id}", status_code=status.HTTP_200_OK, response_model=NewsRead)
async def update_news(
    news_id: int,
    title: str = Form(...),
    text: str = Form(...),
    image: Optional[UploadFile] = File(None),
    news_service: NewsService = Depends(news_service_factory),
    user=Depends(get_current_user),
):
    news = await news_service.get_news_by_id(news_id)
    news_data = NewsUpdate(title=title, text=text)
    return await news_service.update_news(user, news, news_data, image)


@router.get(
    "", status_code=status.HTTP_200_OK, response_model=PaginatedResponse[NewsRead]
)
async def get_all_news(
    news_service: NewsService = Depends(news_service_factory),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    total, news = await news_service.get_all_news(offset, limit)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": news,
    }


@router.get("/{news_id}", status_code=status.HTTP_200_OK, response_model=NewsRead)
async def get_news(
    news_id: int,
    news_service: NewsService = Depends(news_service_factory),
):
    return await news_service.get_news_by_id(news_id)


@router.delete(
    "/{news_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_news(
    news_id: int,
    user: User = Depends(get_current_user),
    news_service: NewsService = Depends(news_service_factory),
):
    await news_service.delete_news(user, news_id)
    return
