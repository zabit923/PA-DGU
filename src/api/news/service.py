import os
from typing import List, Optional, Tuple

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config import media_dir
from core.database import get_async_session
from core.database.models import News, User
from core.database.repositories import NewsRepository
from core.utils import save_file

from .schemas import NewsCreate, NewsUpdate


class NewsService:
    def __init__(self, repository: NewsRepository):
        self.repository = repository

    async def get_news_by_id(self, news_id: int) -> News:
        news = await self.repository.get_by_id(news_id)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News not found"
            )
        return news

    async def get_all_news(
        self, offset: int = 0, limit: int = 10
    ) -> Tuple[int, List[News]]:
        return await self.repository.get_all(offset=offset, limit=limit)

    async def create_news(
        self, user: User, news_data: NewsCreate, image_file: Optional[UploadFile]
    ) -> News:
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
            )
        news_data_dict = news_data.model_dump()
        new_news = News(**news_data_dict)
        new_news.image = await save_file(image_file) if image_file else None
        await self.repository.add(new_news)
        return new_news

    async def update_news(
        self,
        user: User,
        news: News,
        news_data: NewsUpdate,
        image_file: Optional[UploadFile],
    ) -> News:
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
            )
        if image_file:
            await self._update_news_image(user, image_file)
        news_data_dict = news_data.model_dump(exclude_unset=True, exclude_none=True)
        for key, value in news_data_dict.items():
            setattr(news, key, value)
        await self.repository.update(news)
        return news

    @staticmethod
    async def _update_news_image(news: News, image_file: UploadFile) -> None:
        if news.image:
            old_image_path = os.path.join(media_dir, news.image)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        news.image = await save_file(image_file)

    async def delete_news(self, user: User, news_id: int) -> None:
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin"
            )
        news = await self.get_news_by_id(news_id)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News not found"
            )
        await self.repository.delete(news)


def news_service_factory(
    session: AsyncSession = Depends(get_async_session),
) -> NewsService:
    return NewsService(NewsRepository(session))
