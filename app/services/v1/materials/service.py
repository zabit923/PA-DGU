from typing import List, Optional, Tuple

from botocore.exceptions import ClientError
from core.exceptions import (
    ForbiddenError,
    GroupNotFoundError,
    LectureNotFoundError,
    StorageError,
)
from core.integrations.storage import CommonS3DataManager
from fastapi import UploadFile
from models import Lecture, User
from schemas import (
    LectureCreateSchema,
    LectureListResponseSchema,
    LectureUpdateSchema,
    PaginationParams,
)
from services.v1.groups.data_manager import GroupDataManager
from services.v1.groups.service import GroupService
from services.v1.materials.data_manager import LectureDataManager
from services.v1.notifications.service import NotificationService
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.v1.base import BaseService


class LectureService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        s3_data_manager: Optional[CommonS3DataManager] = None,
    ):
        super().__init__(session)
        self.lecture_data_manager = LectureDataManager(session)
        self.group_data_manager = GroupDataManager(session)
        self.s3_data_manager = s3_data_manager

    async def get_by_id(self, lecture_id: int) -> Lecture:
        lecture = await self.lecture_data_manager.get_lecture_by_id(lecture_id)
        if not lecture:
            raise LectureNotFoundError(detail="Лекция не найдена.")
        return lecture

    async def get_my_lectures(
        self,
        user: User,
        pagination: PaginationParams,
    ) -> Tuple[List[LectureListResponseSchema], int]:
        lectures, total = await self.lecture_data_manager.get_my_lectures(
            user, pagination
        )
        return lectures, total

    async def get_by_author_id(
        self,
        author_id: int,
        group_id: int,
        user: User,
        pagination: PaginationParams,
    ) -> Tuple[List[LectureListResponseSchema], int]:
        if not await GroupService(self.session).contrained_user_in_group(
            user, group_id
        ):
            raise ForbiddenError(detail="Вы не являетесь участником этой группы.")
        lectures, total = await self.lecture_data_manager.get_by_author(
            author_id, group_id, pagination
        )
        return lectures, total

    async def get_by_group_id(
        self,
        group_id: int,
        user: User,
        pagination: PaginationParams,
    ) -> Tuple[List[LectureListResponseSchema], int]:
        if not await GroupService(self.session).contrained_user_in_group(
            user, group_id
        ):
            raise ForbiddenError(detail="Вы не являетесь участником этой группы.")
        lectures, total = await self.lecture_data_manager.get_by_group(
            group_id, pagination
        )
        return lectures, total

    async def create_lecture(
        self,
        lecture_data: LectureCreateSchema,
        user: User,
        file: Optional[UploadFile] = None,
    ) -> Lecture:
        file_url = None
        if not user.is_teacher:
            raise ForbiddenError(detail="Вы не являетесь преподавателем.")
        groups = await self.group_data_manager.groups_in_lecture_data(lecture_data)
        if len(groups) != len(lecture_data.groups):
            raise GroupNotFoundError(detail="Некоторые группы не были найдены.")
        if file:
            file_content = await file.read()
            try:
                file_url = await self.s3_data_manager.process_file(
                    "",
                    file=file,
                    key="lecture_files",
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
        else:
            lecture = await self.lecture_data_manager.create(
                user, lecture_data, groups, file_url
            )
            await NotificationService(self.session).create_lecture_notification(lecture)
            return lecture

    async def update_lecture(
        self,
        lecture_id: int,
        lecture_data: LectureUpdateSchema,
        user: User,
        file: Optional[UploadFile] = None,
    ) -> Lecture:
        file_url = None
        groups = None
        lecture = await self.lecture_data_manager.get_lecture_by_id(lecture_id)
        if not lecture:
            raise LectureNotFoundError(detail="Лекция не найдена.")
        if not user.is_teacher:
            raise ForbiddenError(detail="Вы не являетесь преподавателем.")
        if user != lecture.author:
            raise ForbiddenError(detail="Вы не являетесь автором.")
        if file:
            file_content = await file.read()
            old_file_url = None
            if hasattr(lecture, "file") and lecture.file:
                old_file_url = lecture.file
                self.logger.info("Текущее изображение: %s", old_file_url)
            else:
                self.logger.info("Изображение не установлено")
            try:
                file_url = await self.s3_data_manager.process_file(
                    old_file_url=old_file_url if old_file_url else "",
                    file=file,
                    key="lecture_files",
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
        if lecture_data.groups:
            groups = await self.group_data_manager.groups_in_lecture_data(lecture_data)
            if len(groups) != len(lecture_data.groups):
                raise GroupNotFoundError(detail="Некоторые группы не были найдены.")
        await self.lecture_data_manager.update_lecture(
            lecture, lecture_data, groups, file_url
        )
        return lecture

    async def delete_lecture(self, user: User, lecture_id: int) -> None:
        lecture = await self.lecture_data_manager.get_lecture_by_id(lecture_id)
        if not lecture:
            raise LectureNotFoundError(detail="Лекция не найдена.")
        if not user.is_teacher:
            raise ForbiddenError(detail="Вы не являетесь преподавателем.")
        if user != lecture.author:
            raise ForbiddenError(detail="Вы не являетесь автором.")
        await self.lecture_data_manager.delete_item(lecture.id)
