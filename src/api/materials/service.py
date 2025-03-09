import os

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.groups.service import GroupService
from api.materials.schemas import LectureCreate, LectureUpdate
from api.notifications.service import NotificationService
from config import media_dir
from core.database import get_async_session
from core.database.models import Lecture, User
from core.database.repositories import GroupRepository, MaterialRepository
from core.utils import save_file


class LectureService:
    def __init__(
        self,
        material_repository: MaterialRepository,
        group_repository: GroupRepository,
    ):
        self.material_repository = material_repository
        self.group_repository = group_repository

    async def get_by_id(self, lecture_id: int) -> Lecture:
        lecture = await self.material_repository.get_by_id(lecture_id)
        if not lecture:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return lecture

    async def get_my_lectures(self, user: User) -> Sequence[Lecture]:
        if not user.is_teacher:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        lectures = await self.material_repository.get_my_lectures(user)
        return lectures

    async def get_by_author_id(
        self, author_id: int, group_id: int, user: User, group_service: GroupService
    ) -> Sequence[Lecture]:
        if not await group_service.contrained_user_in_group(user, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not member of this group.",
            )
        lectures = await self.material_repository.get_by_author(author_id, group_id)
        return lectures

    async def get_by_group_id(
        self, group_id: int, user: User, group_service: GroupService
    ) -> Sequence[Lecture]:
        if not await group_service.contrained_user_in_group(user, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not member of this group.",
            )
        lectures = await self.material_repository.get_by_group(group_id)
        return lectures

    async def create_lecture(
        self,
        lecture_data: LectureCreate,
        file: UploadFile,
        user: User,
        notification_service: NotificationService,
    ) -> Lecture:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        if file:
            file_name = await save_file(file)
            lecture = Lecture(
                title=lecture_data.title,
                text=lecture_data.text,
                author_id=user.id,
                file=file_name,
            )
        else:
            lecture = Lecture(
                title=lecture_data.title,
                text=lecture_data.text,
                author_id=user.id,
            )
        groups = await self.group_repository.groups_in_lecture_data(lecture_data)
        if len(groups) != len(lecture_data.groups):
            raise HTTPException(status_code=400, detail="Some groups not found.")
        await self.material_repository.create(lecture, groups)
        await notification_service.create_lecture_notification(lecture)
        return lecture

    async def update_lecture(
        self,
        lecture: Lecture,
        lecture_data: LectureUpdate,
        file: UploadFile,
        user: User,
    ) -> Lecture:
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not teacher."
            )
        if user != lecture.author:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="You are not author."
            )
        if file:
            old_file_path = os.path.join(media_dir, lecture.file)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            lecture.file = await save_file(file)
        if lecture_data.groups:
            groups = await self.group_repository.groups_in_lecture_data(lecture_data)
            if len(groups) != len(lecture_data.groups):
                raise HTTPException(status_code=400, detail="Some groups not found.")
            current_groups = {group.id for group in lecture.groups}
            groups_to_remove = current_groups - set(lecture_data.groups)
            groups_to_add = set(lecture_data.groups) - current_groups

            for group_id in groups_to_remove:
                group = next(group for group in lecture.groups if group.id == group_id)
                lecture.groups.remove(group)
            for group_id in groups_to_add:
                group = next(group for group in groups if group.id == group_id)
                lecture.groups.append(group)

        if lecture_data.title:
            lecture.title = lecture_data.title
        if lecture_data.text:
            lecture.text = lecture_data.text
        await self.material_repository.update(lecture)
        return lecture

    async def delete_lecture(self, user: User, lecture_id: int) -> None:
        lecture = await self.material_repository.get_by_id(lecture_id)
        if not user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not teacher or admin.",
            )
        if user != lecture.author:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the author of this lecture.",
            )
        if lecture.file:
            file_path = os.path.join(media_dir, lecture.file)
            if os.path.exists(file_path):
                os.remove(file_path)
        await self.material_repository.delete(lecture)


def lecture_service_factory(
    session: AsyncSession = Depends(get_async_session),
) -> LectureService:
    return LectureService(MaterialRepository(session), GroupRepository(session))
