from typing import List, Optional, Tuple

from botocore.exceptions import ClientError
from app.core.exceptions import (
    CategoryNotFoundError,
    ForbiddenError,
    NewsNotFoundError,
    StorageError,
)
from app.core.integrations.storage import CommonS3DataManager
from fastapi import UploadFile
from app.models import News, User
from app.schemas import (
    NewsCreateSchema,
    NewsListResponseSchema,
    NewsResponseSchema,
    NewsUpdateSchema,
    PaginationParams,
)
from app.services.v1.base import BaseService
from app.services.v1.categories.data_manager import CategoryDataManager
from app.services.v1.news.data_manager import NewsDataManager
from sqlalchemy.ext.asyncio import AsyncSession


class NewsService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        s3_data_manager: Optional[CommonS3DataManager] = None,
    ):
        super().__init__(session)
        self.news_data_manager = NewsDataManager(session)
        self.category_data_manager = CategoryDataManager(session)
        self.s3_data_manager = s3_data_manager

    async def get_news_by_id(self, news_id: int) -> News:
        news = await self.news_data_manager.get_news_by_id(news_id)
        if not news:
            raise NewsNotFoundError(detail="Новость не найдена.")
        return news

    async def get_all_news(
        self,
        pagination: PaginationParams,
        search: str = None,
        category_id: Optional[int] = None,
    ) -> Tuple[List[NewsListResponseSchema], int]:
        news, total = await self.news_data_manager.get_all_news(
            pagination, category_id, search
        )
        return [NewsResponseSchema.model_validate(news) for news in news], total

    async def create_news(
        self, user: User, news_data: NewsCreateSchema, file: Optional[UploadFile] = None
    ) -> News:
        file_url = None
        if not user.is_superuser:
            raise NewsNotFoundError(detail="Вы не являетесь администратором.")
        if news_data.category_id:
            category = await self.category_data_manager.get_category_by_id(
                news_data.category_id
            )
            if not category:
                raise CategoryNotFoundError(detail="Категория не найдена.")
        if file:
            file_content = await file.read()
            try:
                file_url = await self.s3_data_manager.process_file(
                    "",
                    file=file,
                    key="news_images",
                    file_content=file_content,
                )
                self.logger.info("Файл загружен: %s", file_url)
            except ClientError as e:
                self.logger.error("Ошибка S3 при загрузке файла: %s", str(e))
                raise StorageError(detail=f"Ошибка хранилища: {str(e)}")
            except ValueError as e:
                self.logger.error("Ошибка валидации при загрузке файла: %s", str(e))
                raise StorageError(detail=str(e))
            except Exception as e:
                self.logger.error("Неизвестная ошибка при загрузке файла: %s", str(e))
                raise StorageError(detail=f"Ошибка при загрузке файла: {str(e)}")
        new_news = await self.news_data_manager.create_news(
            data=news_data, image_url=file_url
        )
        return new_news

    async def update_news(
        self,
        news_id: int,
        news_data: NewsUpdateSchema,
        user: User,
        image: Optional[UploadFile] = None,
    ) -> News:
        image_url = None
        news = await self.news_data_manager.get_news_by_id(news_id)
        if not news:
            raise NewsNotFoundError(detail="Новость не найдена.")
        if not user.is_superuser:
            raise ForbiddenError(detail="Вы не являетесь администратором.")
        if image:
            file_content = await image.read()
            old_image_url = None
            if hasattr(news, "image") and news.image:
                old_image_url = news.image
                self.logger.info("Текущее изображение: %s", old_image_url)
            else:
                self.logger.info("Изображение не установлено")
            try:
                image_url = await self.s3_data_manager.process_file(
                    old_file_url=old_image_url if old_image_url else "",
                    file=image,
                    key="news_images",
                    file_content=file_content,
                )
                self.logger.info("Файл загружен: %s", image_url)
            except ClientError as e:
                self.logger.error("Ошибка S3 при загрузке файла: %s", str(e))
                raise StorageError(detail=f"Ошибка хранилища: {str(e)}")
            except ValueError as e:
                self.logger.error("Ошибка валидации при загрузке файла: %s", str(e))
                raise StorageError(detail=str(e))
            except Exception as e:
                self.logger.error("Неизвестная ошибка при загрузке файла: %s", str(e))
        await self.news_data_manager.update_news(news, news_data, image_url)
        return news

    async def delete_news(self, user: User, news_id: int) -> None:
        news = await self.news_data_manager.get_news_by_id(news_id)
        if not news:
            raise NewsNotFoundError(detail="Новость не найдена.")
        if not user.is_superuser:
            raise ForbiddenError(detail="Вы не являетесь администратором.")
        await self.news_data_manager.delete_item(news.id)
