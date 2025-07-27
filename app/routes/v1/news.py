from typing import Optional

from core.dependencies import get_db_session
from core.integrations.storage import CommonS3DataManager, get_common_s3_manager
from core.security.auth import get_current_user
from fastapi import Depends, File, Form, Query, UploadFile
from models import User
from routes.base import BaseRouter
from schemas import (
    NewsCreateSchema,
    NewsListResponseSchema,
    NewsResponseSchema,
    NewsUpdateSchema,
    PaginationParams,
)
from services.v1.news.service import NewsService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


class NewsRouter(BaseRouter):
    def __init__(self):
        super().__init__(prefix="news", tags=["News"])

    def configure(self):
        @self.router.post(
            "", status_code=status.HTTP_201_CREATED, response_model=NewsResponseSchema
        )
        async def add_news(
            title: str,
            text: str,
            time_to_read: int,
            category_id: int = None,
            image: UploadFile = File(None),
            s3_data_manager: CommonS3DataManager = Depends(get_common_s3_manager),
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            news_data = NewsCreateSchema(
                title=title,
                text=text,
                time_to_read=time_to_read,
                category_id=category_id,
            )
            new_news = await NewsService(session, s3_data_manager).create_news(
                user, news_data, image
            )
            return new_news

        @self.router.patch(
            "/{news_id}",
            status_code=status.HTTP_200_OK,
            response_model=NewsResponseSchema,
        )
        async def update_news(
            news_id: int,
            title: str = Form(None),
            text: str = Form(None),
            time_to_read: int = Form(None),
            category_id: int = Form(None),
            image: UploadFile = File(None),
            s3_data_manager: CommonS3DataManager = Depends(get_common_s3_manager),
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            news_data = NewsUpdateSchema(
                title=title,
                text=text,
                time_to_read=time_to_read,
                category_id=category_id,
            )
            updated_news = await NewsService(session, s3_data_manager).update_news(
                news_id, news_data, user, image
            )
            return updated_news

        @self.router.get(
            "", status_code=status.HTTP_200_OK, response_model=NewsListResponseSchema
        )
        async def get_news_list(
            skip: int = Query(0, ge=0, description="Количество пропускаемых элементов"),
            limit: int = Query(
                10, ge=1, le=100, description="Количество элементов на странице"
            ),
            search: Optional[str] = Query(
                None, description="Поиск по названию новости"
            ),
            category_id: Optional[int] = Query(
                None, description="ID категории для фильтрации новостей"
            ),
            session: AsyncSession = Depends(get_db_session),
        ):
            """
            ### Args:
            * **skip**: Количество пропускаемых элементов
            * **limit**: Количество элементов на странице (от 1 до 100)
            * **search**: Строка для поиска по названию новости
            * **category_id**: ID категории для фильтрации новостей
            """
            pagination = PaginationParams(skip=skip, limit=limit)
            news, total = await NewsService(session).get_all_news(
                pagination, search, category_id
            )
            page = {
                "items": news,
                "total": total,
                "page": pagination.page,
                "size": pagination.limit,
            }
            return NewsListResponseSchema(data=page)

        @self.router.get(
            "/{news_id}",
            status_code=status.HTTP_200_OK,
            response_model=NewsResponseSchema,
        )
        async def get_news(
            news_id: int,
            session: AsyncSession = Depends(get_db_session),
        ):
            news = await NewsService(session).get_news_by_id(news_id)
            return news

        @self.router.delete(
            "/{news_id}",
            status_code=status.HTTP_204_NO_CONTENT,
        )
        async def delete_news(
            news_id: int,
            user: User = Depends(get_current_user),
            session: AsyncSession = Depends(get_db_session),
        ):
            await NewsService(session).delete_news(user, news_id)
            return
