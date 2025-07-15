from typing import List, Optional

from botocore.exceptions import ClientError
from core.exceptions import InvalidFileTypeError, StorageError
from core.integrations.storage import CommonS3DataManager
from fastapi import UploadFile
from models import User
from redis import Redis
from schemas import UserUpdateResponseSchema
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError
from app.core.integrations.cache.auth import AuthRedisDataManager
from app.schemas import PaginationParams, UserReadSchema, UserSchema
from app.services.v1.base import BaseService
from app.services.v1.users.data_manager import UserDataManager


class UserService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        redis: Redis = None,
        s3_data_manager: Optional[CommonS3DataManager] = None,
    ):
        super().__init__(session)
        self.data_manager = UserDataManager(session)
        self.redis_data_manager = AuthRedisDataManager(redis)
        self.s3_data_manager = s3_data_manager

    async def get_users(
        self,
        pagination: PaginationParams,
        search: str = None,
        current_user: User = None,
    ) -> tuple[List[UserSchema], int]:
        if not current_user.is_superuser:
            raise ForbiddenError(
                detail="Только администраторы и модераторы могут просматривать список пользователей",
            )

        users, total = await self.data_manager.get_users(
            pagination=pagination,
            search=search,
        )

        for user in users:
            user.is_online = await self.redis_data_manager.get_online_status(user.id)

        return users, total

    async def update_user(
        self, user: UserReadSchema, user_data: User, image_file: Optional[UploadFile]
    ) -> UserUpdateResponseSchema:
        if image_file:
            await self._update_user_image(user, image_file)
        await self.data_manager.update_user(user, user_data)
        return UserUpdateResponseSchema(data=UserReadSchema.model_validate(user))

    async def _update_user_image(
        self,
        user: User,
        file: UploadFile,
    ) -> None:
        file_content = await file.read()
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise InvalidFileTypeError()
        old_image_url = None
        if hasattr(user, "image") and user.image:
            old_image_url = user.image
            self.logger.info("Текущее изображение: %s", old_image_url)
        else:
            self.logger.info("Изображение не установлено")
        try:
            image_url = await self.s3_data_manager.process_image(
                old_image_url=old_image_url if old_image_url else "",
                file=file,
                key="user_images",
                file_content=file_content,
            )
            self.logger.info("Файл загружен: %s", image_url)
        except ClientError as e:
            self.logger.error("Ошибка S3 при загрузке изображения: %s", str(e))
            raise StorageError(detail=f"Ошибка хранилища: {str(e)}")
        except ValueError as e:
            self.logger.error("Ошибка валидации при загрузке изображения: %s", str(e))
            raise StorageError(detail=str(e))
        except Exception as e:
            self.logger.error("Неизвестная ошибка при загрузке изображения: %s", str(e))
            raise StorageError(detail=f"Ошибка при загрузке изображения: {str(e)}")

        await self.data_manager.update_image(user, image_url)

    async def change_online_status(self, user: User) -> UserReadSchema:
        if user.is_online:
            await self.data_manager.update_item(user.id, {"is_online": False})
        else:
            await self.data_manager.update_item(user.id, {"is_online": True})
        return user

    async def change_ignore_status(self, user: User) -> UserReadSchema:
        if user.ignore_messages:
            await self.data_manager.update_item(user.id, {"ignore_messages": False})
        else:
            await self.data_manager.update_item(user.id, {"ignore_messages": True})
        return user
